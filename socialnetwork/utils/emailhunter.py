from pyhunter import PyHunter

hunter = PyHunter('67f0821fcec2d4476f16e633e5aceef036928682')


def check_email(email):
    global hunter
    result = hunter.email_verifier(email)
    if int(result['score']) > 40:
        return True
    return False
