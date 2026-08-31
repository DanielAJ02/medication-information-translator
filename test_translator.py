from ai_translator import AITranslator

translator = AITranslator()

text = "This medication may cause gastrointestinal bleeding and should be administered according to the prescribed dosage."

result = translator.translate(text)

print(result)