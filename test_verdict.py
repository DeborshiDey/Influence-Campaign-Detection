
import re

def parse_verdict(content):
    # 1. Explicit DFRAC Analysis/Verdict line (Strongest signal)
    explicit_patterns = [
        r'DFRAC Analysis:\s*([A-Za-z\s]+?)(?:\n|$)',
        r'Verdict:\s*([A-Za-z\s]+?)(?:\n|$)',
        r'Conclusion:\s*([A-Za-z\s]+?)(?:\n|$)'
    ]
    
    for pattern in explicit_patterns:
        match = re.search(pattern, content, re.I)
        if match:
            candidate = match.group(1).strip().lower()
            # Filter out common non-verdict words that might be caught
            if candidate not in ['the', 'in', 'a', 'this', 'we', 'upon']:
                # Check if it contains key verdict words
                if any(w in candidate for w in ['fake', 'misleading', 'true', 'false']):
                    return candidate.title()

    # 2. Look for verdict in the Conclusion paragraph
    conclusion_match = re.search(r'Conclusion[:\s]+(.*?)(?:Share this|DFRAC Analysis|$)', content, re.S | re.I)
    if conclusion_match:
        conclusion_text = conclusion_match.group(1).lower()
        
        # Priority keywords
        if 'fake' in conclusion_text:
            return 'Fake'
        if 'misleading' in conclusion_text:
            return 'Misleading'
        if 'false' in conclusion_text:
            return 'False'
        if 'true' in conclusion_text:
            return 'True'

    # 3. Look for "Misleading-en" style tags at start
    if 'misleading-en' in content.lower():
        return 'Misleading'
    if 'fake-en' in content.lower():
        return 'Fake'

    return "Unknown"

# Test Cases
content1 = """Viral Classroom Video Claiming ‘Islamic Indoctrination’ found to be Fake
...
Conclusion
The viral video claiming that children in a British classroom were being “indoctrinated into Islam” is digitally altered. There is no evidence linking the footage to any school, and the visual inconsistencies confirm it is a manipulated clip.
DFRAC Analysis: Fake
Share this…"""

content2 = """Allahabad High Court video falsely shared as a Supreme Court protest against vote theft
...
Conclusion:
The DFRAC fact check makes it clear that the video shared on social media is not of lawyers marching in the Supreme Court against vote theft. This video is of lawyers appealing for votes during the Bar Association election at the Allahabad High Court. Therefore, the users’ claim is misleading.
Share this…"""

print(f"Content 1 Verdict: {parse_verdict(content1)}")
print(f"Content 2 Verdict: {parse_verdict(content2)}")
