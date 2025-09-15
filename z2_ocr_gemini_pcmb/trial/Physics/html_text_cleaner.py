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
    text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
    text = text.strip()  # Remove leading/trailing whitespace
    
    return text


def clean_html_to_text_beautifulsoup(html_content):
    """
    Alternative implementation using BeautifulSoup for more robust HTML parsing.
    
    Args:
        html_content (str): HTML content as a string
        
    Returns:
        str: Clean plain text with HTML tags removed and entities decoded
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        # Fallback to regex method if BeautifulSoup is not available
        return clean_html_to_text(html_content)
    
    if not html_content:
        return ""
    
    # Remove outer quotes if present
    text = html_content.strip('"\'')
    
    # Handle escaped quotes in the string
    text = text.replace('\\"', '"').replace("\\'", "'")
    
    # Handle common escape sequences
    text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    
    # Extract text content
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


# Simplified function for most common use cases
def extract_text_from_html(html_string):
    """
    Simple function to extract plain text from HTML string.
    This is the recommended function for general use.
    
    Args:
        html_string (str): HTML content as a string
        
    Returns:
        str: Clean plain text
    """
    return clean_html_to_text_beautifulsoup(html_string)


# Example usage and test
if __name__ == "__main__":
    # Test with the provided example
    test_html = '"<div style=\\"text-align:justify\\">With advancing age of a person the loss of the&nbsp;ability of eye to focus on near and far objects is called</div>\\n"'
    
    print("Original HTML:")
    print(repr(test_html))
    print("\nCleaned text (regex method):")
    result1 = clean_html_to_text(test_html)
    print(repr(result1))
    print("Display:", result1)
    print("\nCleaned text (BeautifulSoup method):")
    result2 = clean_html_to_text_beautifulsoup(test_html)
    print(repr(result2))
    print("Display:", result2)
    print("\nSimplified function:")
    result3 = extract_text_from_html(test_html)
    print(repr(result3))
    print("Display:", result3) 