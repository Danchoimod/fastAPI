#Helper Classes 

def generate_slug(title: str) -> str:
    """Biến tiêu đề thành đường dẫn URL đẹp"""
    import re
    return re.sub(r'\W+', '-', title.lower()).strip('-')