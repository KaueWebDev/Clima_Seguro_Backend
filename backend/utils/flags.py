def get_flag_url(country_code):
    if not country_code:
        return ""
    return f"https://flagcdn.com/w80/{country_code.lower()}.png"
