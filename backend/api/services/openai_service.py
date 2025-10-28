from openai import OpenAI
from django.conf import settings
import json
import httpx
# import logging  # maybe use this for better tracking


class OpenAIService:
    
    def __init__(self):
        # Workaround for proxy issues - see https://github.com/openai/openai-python/issues/...
        try:
            http_client = httpx.Client()
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                http_client=http_client
            )
        except:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        self.model = "gpt-4o-mini"
        self.timeout = 30
    
    def generate_coach_summary(self, metrics):
        prompt = self._build_coach_prompt(metrics)
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You're a no-excuses health coach. Return JSON only. Be direct with numbers.\n\n{\"summary\": \"one sentence calling out the trend\", \"receipts\": [\"HRV 42→55, +31%\"], \"why_it_matters\": \"quick connection to energy/focus\", \"moves_for_this_week\": {\"non_negotiables\": [\"specific actions with targets\"], \"training\": \"readiness to workout intensity\", \"nutrition\": \"protein/hydration numbers\", \"recovery\": \"cold/heat/mobility\"}, \"watchouts\": [\"red flags\"], \"one_percent_upgrade\": \"tiny habit with when/where\", \"if_data_missing\": {\"reason_for_gap\": \"what's missing\", \"quick_fix\": \"how to fix\"}}\n\nBe hype, use numbers, call out flat metrics."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.45,
                max_tokens=400,
                timeout=self.timeout
            )
            
            content = resp.choices[0].message.content
            result = self._parse_json_safely(content)
            
            if not result:
                print(f"Failed to parse: {content[:200]}")
                return self._fallback_coach_summary()
            
            return result
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_coach_summary()
    
    def generate_trend_insight(self, metrics):
        prompt = self._build_trend_prompt(metrics)
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze health trends. Return JSON format:
{"summary": "one specific sentence about the main trend", "takeaways": ["specific observation with numbers", "pattern or concern to watch"]}

Look for: improving/declining scores, day-to-day volatility, recovery patterns. Call out specific days if they're outliers. Be data-driven."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150,
                timeout=self.timeout
            )
            
            content = resp.choices[0].message.content
            result = self._parse_json_safely(content)
            
            if not result:
                return self._fallback_trend_insight()
            
            return result
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_trend_insight()
    
    def generate_chat_response(self, message, metrics):
        ctx = self._build_context(metrics)
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You're a wellness coach with access to their Oura data. Answer in 2-3 sentences max using their actual numbers. Be specific and practical. No medical advice.

Their recent data:
{ctx}"""
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=150,
                timeout=self.timeout
            )
            
            return {"response": resp.choices[0].message.content}
            
        except:
            return {"response": "I'm having trouble processing that question right now. Please try again."}
    
    def _build_coach_prompt(self, metrics):
        if not metrics:
            return "No data available."
        
        # calculate averages
        avg_r = sum(m.get('readiness_score', 0) or 0 for m in metrics) / len(metrics)
        avg_s = sum(m.get('sleep_score', 0) or 0 for m in metrics) / len(metrics)
        avg_a = sum(m.get('activity_score', 0) or 0 for m in metrics) / len(metrics)
        avg_sleep_hrs = sum(m.get('sleep_duration', 0) or 0 for m in metrics) / len(metrics)
        avg_hrv = sum(m.get('hrv', 0) or 0 for m in metrics) / len(metrics) if any(m.get('hrv') for m in metrics) else 0
        avg_steps = sum(m.get('steps', 0) or 0 for m in metrics) / len(metrics) if any(m.get('steps') for m in metrics) else 0
        
        # calculate trends (first 3 days vs last 3 days)
        if len(metrics) >= 6:
            early_r = sum(m.get('readiness_score', 0) or 0 for m in metrics[:3]) / 3
            late_r = sum(m.get('readiness_score', 0) or 0 for m in metrics[-3:]) / 3
            trend = "improving" if late_r > early_r + 2 else "declining" if late_r < early_r - 2 else "stable"
        else:
            trend = "stable"
        
        return f"""7-day summary:
- Readiness: {avg_r:.0f}/100 ({trend})
- Sleep: {avg_s:.0f}/100 ({avg_sleep_hrs:.1f}h average)
- Activity: {avg_a:.0f}/100 ({avg_steps:.0f} steps/day)
- HRV: {avg_hrv:.0f}ms

Daily breakdown:
{self._format_daily_data(metrics)}"""
    
    def _build_trend_prompt(self, metrics):
        if len(metrics) < 2:
            return "Not enough data."
        
        # compare first half to second half
        mid = len(metrics)//2
        first = metrics[:mid]
        second = metrics[mid:]
        
        # readiness trend
        r1 = sum(m.get('readiness_score', 0) or 0 for m in first) / len(first)
        r2 = sum(m.get('readiness_score', 0) or 0 for m in second) / len(second)
        
        # sleep trend
        s1 = sum(m.get('sleep_score', 0) or 0 for m in first) / len(first)
        s2 = sum(m.get('sleep_score', 0) or 0 for m in second) / len(second)
        
        # activity trend
        a1 = sum(m.get('activity_score', 0) or 0 for m in first) / len(first)
        a2 = sum(m.get('activity_score', 0) or 0 for m in second) / len(second)
        
        return f"""Week comparison (first half vs second half):
Readiness: {r1:.0f} → {r2:.0f} ({r2-r1:+.0f})
Sleep: {s1:.0f} → {s2:.0f} ({s2-s1:+.0f})
Activity: {a1:.0f} → {a2:.0f} ({a2-a1:+.0f})

Daily progression:
{self._format_daily_data(metrics)}"""
    
    def _build_context(self, metrics):
        if not metrics:
            return "No recent data available."
        
        # summary for chat context
        avg_r = sum(m.get('readiness_score', 0) or 0 for m in metrics) / len(metrics)
        avg_s = sum(m.get('sleep_score', 0) or 0 for m in metrics) / len(metrics)
        avg_sleep_hrs = sum(m.get('sleep_duration', 0) or 0 for m in metrics) / len(metrics)
        avg_hrv = sum(m.get('hrv', 0) or 0 for m in metrics) / len(metrics) if any(m.get('hrv') for m in metrics) else 0
        
        latest = metrics[0] if metrics else {}
        
        return f"""7-day averages: Readiness {avg_r:.0f}, Sleep {avg_s:.0f} ({avg_sleep_hrs:.1f}h), HRV {avg_hrv:.0f}ms
Latest day: R:{latest.get('readiness_score', 'N/A')} S:{latest.get('sleep_score', 'N/A')} ({latest.get('sleep_duration', 0):.1f}h)"""
    
    def _format_daily_data(self, metrics):
        lines = []
        for m in metrics[-7:]:
            sleep_hrs = m.get('sleep_duration', 0)
            lines.append(
                f"- {m.get('date')}: R:{m.get('readiness_score', 'N/A')} "
                f"S:{m.get('sleep_score', 'N/A')}({sleep_hrs:.1f}h) "
                f"A:{m.get('activity_score', 'N/A')}"
            )
        return '\n'.join(lines)
    
    def _parse_json_safely(self, content):
        # GPT sometimes wraps JSON in markdown blocks
        try:
            # Handle markdown wrapping
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            return json.loads(content.strip())
        except Exception as e:
            # print(f"Failed to parse: {content}")
            return None
    
    def _fallback_coach_summary(self):
        # return something if API fails
        return {
            "summary": "Unable to generate personalized insights right now. Your data is being tracked.",
            "receipts": [],
            "moves_for_this_week": {
                "non_negotiables": ["Focus on consistent sleep times", "Aim for 7-8 hours of sleep"]
            }
        }
    
    def _fallback_trend_insight(self):
        return {
            "summary": "Your metrics look stable this week.",
            "takeaways": ["Keep doing what you're doing", "Stay consistent"]
        }

