import re
import html


def clean_html_to_text(html_content):
    """
    Remove HTML tags and decode HTML entities to extract plain text.
    
    Args:
        html_content (str): HTML content as a string
        
    Returns:
        str: Clean plain text with HTML tags removed and entities decoded
    """
    if not html_content:
        return ""
    
    # Remove outer quotes if present
    text = html_content.strip('"\'')
    
    # Handle escaped quotes in the string
    text = text.replace('\\"', '"').replace("\\'", "'")
    
    # Decode HTML entities (like &nbsp;, &amp;, etc.)
    text = html.unescape(text)
    
    # Remove HTML tags using regex
    text = re.sub(r'<[^>]+>', '', text)
    
    # Handle common escape sequences
    text = text.replace('\\n', '').replace('\\t', ' ').replace('\\r', '')
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
    text = text.strip()  # Remove leading/trailing whitespace
    
    return text


def clean_html_to_text_beautifulsoup(html_content):
    """
    Alternative implementation using BeautifulSoup for more robust HTML parsing.
    Requires: pip install beautifulsoup4
    
    Args:
        html_content (str): HTML content as a string
        
    Returns:
        str: Clean plain text with HTML tags removed and entities decoded
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("BeautifulSoup not available. Install with: pip install beautifulsoup4")
        # Fallback to regex method if BeautifulSoup is not available
        return clean_html_to_text(html_content)
    
    if not html_content:
        return ""
    
    # Remove outer quotes if present
    text = html_content.strip('"\'')
    
    # Handle escaped quotes in the string
    text = text.replace('\\"', '"').replace("\\'", "'")
    
    # Handle common escape sequences
    text = text.replace('\\n', '').replace('\\t', ' ').replace('\\r', '')
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    
    # Extract text content
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


# Example usage and test
if __name__ == "__main__":
    # Test with the provided example
    test_html = '"<div style=\\"text-align:justify\\">With advancing age of a person the loss of the&nbsp;ability of eye to focus on near and far objects is called</div>\\n"'
    
    print("Original HTML:")
    print(test_html)
    
    print("\nCleaned text (regex method):")
    result1 = clean_html_to_text(test_html)
    print(f"'{result1}'")
    
    print("\nCleaned text (BeautifulSoup method):")
    result2 = clean_html_to_text_beautifulsoup(test_html)
    print(f"'{result2}'")
    
    # Additional test cases
    print("\n" + "="*50)
    print("Additional test cases:")
    
    test_cases = [
        '<p>Simple paragraph</p>',
        '<div>Text with &amp; entities &lt;test&gt;</div>',
        '<span style="color:red">Styled text</span>',
        'Plain text without HTML',
        ''
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = clean_html_to_text(test)
        print(f"Test {i}: '{test}' -> '{result}'") 