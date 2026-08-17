desc_url = first["description"]

response = requests.get(desc_url)

print(response.text[:3000])
