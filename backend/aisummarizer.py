import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()

def generate_detailed_summary(feedback_json: dict) -> str:
    """
    Generate detailed feedback without OpenAI as fallback
    """
    total_reps = feedback_json.get('totalReps', 0)
    perfect_reps = feedback_json.get('perfectFormReps', 0)
    sweet_spot_reps = feedback_json.get('sweetSpotReps', 0)
    rep_metrics = feedback_json.get('repMetrics', [])
    
    if total_reps == 0:
        return "No reps detected. Make sure your full body is visible and you're performing shoulder presses with proper form."
    
    # Build summary
    summary_parts = []
    
    # Overall performance
    summary_parts.append(f"You completed {total_reps} reps.")
    
    if perfect_reps == total_reps:
        summary_parts.append("Excellent work! All reps had perfect form.")
    elif perfect_reps > 0:
        summary_parts.append(f"{perfect_reps} reps had perfect form - keep it up!")
    
    # Analyze common issues
    issues = []
    if rep_metrics:
        avg_min_elbow = sum(r['minElbow'] for r in rep_metrics) / len(rep_metrics)
        avg_max_elbow = sum(r['maxElbow'] for r in rep_metrics) / len(rep_metrics)
        avg_diff = sum(r['maxDiff'] for r in rep_metrics) / len(rep_metrics)
        avg_shoulder = sum(r['maxShoulder'] for r in rep_metrics) / len(rep_metrics)
        
        thresholds = feedback_json.get('thresholds', {})
        sweet_spot_min = thresholds.get('sweetSpotMin', 70)
        sweet_spot_max = thresholds.get('sweetSpotMax', 90)
        
        # Depth issues
        if avg_min_elbow > sweet_spot_max:
            issues.append(f"Go deeper - you're only reaching {avg_min_elbow:.0f}° (aim for {sweet_spot_min}-{sweet_spot_max}°)")
        elif avg_min_elbow < sweet_spot_min:
            issues.append(f"Don't go too deep - you're reaching {avg_min_elbow:.0f}° (aim for {sweet_spot_min}-{sweet_spot_max}°)")
        
        # Extension issues
        if avg_max_elbow < 155:
            issues.append(f"Extend your arms fully at the top (currently {avg_max_elbow:.0f}°)")
        
        # Symmetry issues
        if avg_diff > 20:
            issues.append(f"Your arms are uneven (difference of {avg_diff:.0f}°) - focus on symmetry")
        
        # Elbow flaring
        if avg_shoulder > 180:
            issues.append(f"Your elbows are flaring out - keep them at shoulder level")
    
    if issues:
        summary_parts.append("Areas to improve: " + "; ".join(issues) + ".")
    else:
        summary_parts.append("Your form is looking great!")
    
    return " ".join(summary_parts)

def summarize_feedback(feedback_json: dict) -> str:
    """
    Summarize workout feedback using OpenAI's API or detailed fallback
    """
    # Try OpenAI first if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and api_key.startswith("sk-"):
        try:
            client = OpenAI(api_key=api_key)
            feedback_str = str(feedback_json)

            prompt = (
                "You are a fitness coach AI. Read the following exercise feedback data "
                "from a user's shoulder press workout and summarize it in 3-4 sentences with the number of reps, "
                "giving actionable recommendations for improving form. Do not include any percentages or data, "
                "just tell them what to do and improve:\n\n"
                f"{feedback_str}\n\nSummary:"
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            print(f"OpenAI API failed: {e}")
            # Fall through to detailed fallback
    
    # Use detailed fallback
    return generate_detailed_summary(feedback_json)