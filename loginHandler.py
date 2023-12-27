def checkReq(email, password, username=None):
    if username is not None:
        if not username.strip():
            # Handle the case where username is empty or contains only whitespace
            return "Username is empty."
        if len(username.strip()) > 20:
            return "Username is too long, keep it under 20 symbols."

    if not email.strip():
        # Handle the case where email is empty or contains only whitespace
        return "Email is empty."

    if not password.strip():
        # Handle the case where password is empty or contains only whitespace
        return "Password is empty."
    
    if len(email.strip()) > 50:
        return "Email is too long, keep it under 50 symbols."
    if len(password.strip()) > 50:
        return "Email is too long, keep it under 50 symbols."
    
    return