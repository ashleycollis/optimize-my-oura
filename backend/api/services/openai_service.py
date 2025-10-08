from openai import OpenAI
from django.conf import settings
import json
import httpx
# import logging  # maybe use this for better tracking


class OpenAIService:
    """Handles OpenAI API calls for insights"""
    
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
        self.timeout = 15
    
    def generate_coach_summary(self, metrics):
        """Generate AI coach summary from 7-day metrics"""
        prompt = self._build_coach_prompt(metrics)
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You're a wellness coach helping your client optimize. Be brief and helpful.

Return JSON only:
{"explanation": "brief summary of their week", "suggestions": ["specific tip 1", "specific tip 2"]}

Keep explanation to 1-2 sentences. Give 2 concrete suggestions (not medical advice). Be encouraging but very honest."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
                timeout=self.timeout
            )
            
            content = resp.choices[0].message.content
            # print(f"Got response: {content[:100]}")  # debug
            result = self._parse_json_safely(content)
            
            # Make sure we got valid data back
            if not result or 'explanation' not in result:
                return self._fallback_coach_summary()
            
            return result
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._fallback_coach_summary()
    
    def generate_trend_insight(self, metrics):
        """Generate trend analysis"""
        prompt = self._build_trend_prompt(metrics)
        
        # FIXME: This is similar to coach_summary, maybe consolidate?
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze health trends. Return JSON format:
{"summary": "one sentence about the trend", "takeaways": ["observation 1", "observation 2"]}

Focus on what changed and any patterns you see."""
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
        """Generate response to user question"""
        ctx = self._build_context(metrics)
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You're a wellness coach. Answer questions about their data in 2 sentences max. Don't give medical advice.

User's recent data:
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
        
        # Quick averages
        avg_r = sum(m.get('readiness_score', 0) or 0 for m in metrics) / len(metrics)
        avg_s = sum(m.get('sleep_score', 0) or 0 for m in metrics) / len(metrics)
        avg_a = sum(m.get('activity_score', 0) or 0 for m in metrics) / len(metrics)
        
        # Old format - was too verbose
        # return f"User data:\nReadiness avg: {avg_r}, Sleep avg: {avg_s}..."
        
        return f"""Last 7 days averages:
- Readiness: {avg_r:.0f}
- Sleep: {avg_s:.0f}
- Activity: {avg_a:.0f}

Daily data:
{self._format_daily_data(metrics)}"""
    
    def _build_trend_prompt(self, metrics):
        if len(metrics) < 2:
            return "Not enough data."
        
        # Compare first half to second half
        mid = len(metrics)//2
        first = metrics[:mid]
        second = metrics[mid:]
        
        avg1 = sum(m.get('readiness_score', 0) or 0 for m in first) / len(first)
        avg2 = sum(m.get('readiness_score', 0) or 0 for m in second) / len(second)
        
        change = avg2 - avg1
        
        return f"""Trend analysis:
First half average readiness: {avg1:.0f}
Second half average readiness: {avg2:.0f}
Change: {change:+.0f} points

Daily progression:
{self._format_daily_data(metrics)}"""
    
    def _build_context(self, metrics):
        if not metrics:
            return "No recent data available."
        
        # Quick summary for context
        return f"""Recent averages:
- Readiness: {sum(m.get('readiness_score', 0) or 0 for m in metrics) / len(metrics):.0f}
- Sleep: {sum(m.get('sleep_score', 0) or 0 for m in metrics) / len(metrics):.0f}
- HRV: {sum(m.get('hrv', 0) or 0 for m in metrics) / len(metrics):.0f}ms"""
    
    def _format_daily_data(self, metrics):
        lines = []
        for m in metrics[-7:]:
            lines.append(
                f"- {m.get('date')}: R:{m.get('readiness_score', 'N/A')} "
                f"S:{m.get('sleep_score', 'N/A')} A:{m.get('activity_score', 'N/A')}"
            )
        return '\n'.join(lines)
    
    def _parse_json_safely(self, content):
        """Parse JSON - GPT sometimes wraps it in markdown blocks"""
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
        # Just return something generic if API fails
        return {
            "explanation": "Keep up your current routine and focus on consistency.",
            "suggestions": ["Maintain your sleep schedule", "Stay active"]
        }
    
    def _fallback_trend_insight(self):
        return {
            "summary": "Your metrics look stable this week.",
            "takeaways": ["Keep doing what you're doing", "Stay consistent"]
        }

