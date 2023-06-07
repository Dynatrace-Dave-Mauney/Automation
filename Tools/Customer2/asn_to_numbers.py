test_asn = 'ABZ09'

def convert_asn_to_numbers(asn):
    numbers = ''
    for character in asn.lower():
        if character.isalpha():
            decrement = 96
        else:
            decrement = 18 # Normally it would be 48, but to avoid collisions numbers will be 30 - 39 instead of 00 - 09

        ordinal = ord(character) - decrement
        ordinal_string = f'{ordinal:02}'
        # print(character, ordinal_string)
        numbers += ordinal_string

    return str(numbers)

print(f'{test_asn} = {convert_asn_to_numbers(test_asn)}')
