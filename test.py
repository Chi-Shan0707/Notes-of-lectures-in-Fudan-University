​def vigenere_cipher(a, text, key):
    text = text.upper()
    key = key.upper()

    key = (key * (len(text) // len(key) + 1))[:len(text)]

    result = ""

    for i, char in enumerate(text):
        if char.isalpha():  
            text_pos = ord(char) - ord('A')
            key_pos = ord(key[i]) - ord('A')

            if a == 1:
                new_pos = (text_pos + key_pos) % 26
            else:
                new_pos = (text_pos - key_pos) % 26
                if new_pos < 0:
                    new_pos += 26  # Ensure the position is non-negative

            result += chr(new_pos + ord('A'))
        else:
            result += char

    return result

a = int(input())
text = input()
key = input()

output = vigenere_cipher(a, text, key)
print(output)