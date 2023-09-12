s = "ананас, сыр, майонез, грецкий орех"



def validate_input(user_input):
    # Разбиваем введенный текст на отдельные слова по запятым
    words = user_input.split(',')
    # Проверяем каждое слово
    for word in words:  
        
        if word.isdigit():
            return False
        
    
    return True

print(validate_input(s))