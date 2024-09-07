from encrypt import encrypt_aes

# Przykładowe dane
password = "example_password"
decrypted_aes_key_hex = "e48d4063bd122d72fb0583d0d30577b3bad6d51e751bd34ef3904e346bb2fa41"

password_encrypted = encrypt_aes(password, decrypted_aes_key_hex)
print("Encrypted password:", password_encrypted)