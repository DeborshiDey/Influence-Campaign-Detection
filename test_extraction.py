
import re

def parse_claim_and_fact_check(content):
    # Normalize newlines
    content = content.replace('\r\n', '\n')
    
    # 1. Extract Claim
    # Claims often appear before "Fact Check" header
    claim = "Claim not found"
    
    # Split by "Fact Check" header if present
    parts = re.split(r'\nFact Check\s*\n', content, flags=re.I)
    
    intro_text = parts[0]
    
    # Look for specific claim indicators in intro
    claim_match = re.search(r'(?:claim|allegation|caption|text reads).*?that\s+(.*?)(?:\n\n|\nFact Check|$)', intro_text, re.S | re.I)
    if claim_match:
        claim = claim_match.group(1).strip()
    else:
        # Fallback: Take the first substantial paragraph of intro
        paragraphs = [p.strip() for p in intro_text.split('\n') if len(p.strip()) > 50]
        if paragraphs:
            # Skip title-like first lines if possible
            claim = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]

    # 2. Extract Fact Check Details
    # This is the section AFTER "Fact Check" but BEFORE "Conclusion"
    fact_check = "Fact check details not found"
    
    if len(parts) > 1:
        # We have a Fact Check section
        fc_section = parts[1]
        
        # Stop at Conclusion
        fc_parts = re.split(r'\nConclusion', fc_section, flags=re.I)
        fact_check = fc_parts[0].strip()
    else:
        # Try to find "Investigation" or similar if "Fact Check" header is missing
        investigation_match = re.search(r'(?:investigation|found that|revealed that)(.*?)(?:\nConclusion|$)', content, re.S | re.I)
        if investigation_match:
            fact_check = investigation_match.group(1).strip()

    return claim[:300], fact_check[:300] # Truncate for preview

# Test Data
content1 = """Viral Classroom Video Claiming ‘Islamic Indoctrination’ found to be Fake
Fact Check en
November 19, 2025
Aayushi Rana
A video is circulating online with the allegation that “young white children are being indoctrinated into Islam” and shown “raising their hands and chanting ‘Allahu Akbar’ in a classroom.”
The video looks like it was filmed in an elementary or middle school classroom...
Link
Fact Check
Upon investigation, we found the claim and the video to be fake. A closer examination reveals two clear signs of digital manipulation:
1. The teacher appears to rise from her knees...
Conclusion
The viral video claiming that children in a British classroom were being “indoctrinated into Islam” is digitally altered."""

print("--- Article 1 ---")
c, fc = parse_claim_and_fact_check(content1)
print(f"CLAIM: {c}")
print(f"FACT CHECK: {fc}")
