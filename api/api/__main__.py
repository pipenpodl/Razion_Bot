import pika
import requests
from googletrans import Translator

API_KEY = 'd1f09be3ca0c4b8eacd967d2cf43a274'
# Создаем соединение с RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='api_queue')
channel.queue_declare(queue='bot_queue')


def translate_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, src='ru', dest='en')
    return translated_text.text


def translate_to_russian(text):
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='ru')
    return translated_text.text


def get_recipe_suggestions(ingredients):
    ingredients_english = [translate_to_english(
        ingredient) for ingredient in ingredients]
    ingredients_str = ",".join(ingredients_english)

    try:
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients_str}&number=3&apiKey={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            recipes = response.json()
            for recipe in recipes:
                recipe['title'] = translate_to_russian(recipe['title'])
            return recipes
        else:
            print(f"Ошибка при запросе к API: {response.status_code}")
            return None
    except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NameResolutionError) as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")
        return None


def callback(ch, method, properties, body):
    ingredients = body.decode('utf-8').split(',')

    recipes = get_recipe_suggestions(ingredients)

    if recipes:
        if len(recipes) == 0:
            send_recipe("Нет подходящих рецептов")
        else:
            mes = """Вот 3 рецепта на основе ваших продуктов:\n\n"""
            for idx, recipe in enumerate(recipes, start=1):
                missed_ingredients = [translate_to_russian(ingredient['name']) for ingredient in recipe['missedIngredients']]
                mes = mes + f"{idx}. {recipe['title']} (Недостающие ингредиенты: {', '.join(missed_ingredients)})\n"
            send_recipe(mes)



def send_recipe(message):
    print(f"сообщение {message}")
    channel.basic_publish(exchange='', routing_key='bot_queue', body=message)


def main():
    channel.basic_consume(
        queue='api_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
