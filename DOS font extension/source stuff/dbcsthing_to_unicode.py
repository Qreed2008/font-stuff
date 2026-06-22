from PIL import Image, ImageDraw, ImageFont
import os

img_loc = input("Location of image: ")
img = Image.open(img_loc)

font_size = input("Font size (\"[w]x[h]\" - if multiple, split with \",\"): ")

if len(font_size.split(",")) > 1:
  print("""You gave multiple font sizes.
To select which to use for which blocks of text, you can do [next] to move to the next size (it loops around)
Do note all rows start as the first one""")

font_size = [[int(x) for x in item.split("x")] for item in font_size.split(",")]

img_font = ImageFont.truetype(input("Font for the row text: "), font_size[0][1])

padding = input("Any padding? (\"top,bottom,left,right\") ")
padding = [int(x) for x in padding.split(",")]

print(font_size)

text = []
current = ""
while current != "end" and not current.startswith("load("):
  text.append(input("Line of text (\"end\" will stop this portion, or do load(\"name\") to load ): "))
  current = text[-1]

if current.startswith("load("):
  if len(current.split("load(\"")[1].split(")")[0].split(",")) == 1:
    with open("\"".join(current.split("load(\"")[1].split("\"")[:-1]), "r") as openFile:
      text = openFile.read().split("\n")
  else: # Note: accepted encodings are "utf-8" (default), "utf-16-le", and "utf-16-be" I think, there's also "utf-16" but that just does the LE one
    with open(current.split("load(\"")[1].split("\", ")[0], "r", encoding=(current.split(", \"")[1].split("\"")[0])) as openFile:
      text = openFile.read().split("\n")

del text[-1]

if text[0].startswith(chr(0xFFFE)):
  text[0] = text[0][1:]

char_dump = {}

y = 0
for i in range(len(text)):
  x = 0
  current_size = 0
  j = 0
  while j < len(text[i]):
    if text[i][j:j+6] == "[next]":
      current_size = (current_size + 1) % len(font_size)
      j += 6
    else:
      if text[i][j] not in char_dump:
        char_dump[text[i][j]] = img.crop(( x, y + padding[0], x + font_size[current_size][0], y + font_size[current_size][1] + padding[0] ))

      x += font_size[current_size][0]
      j += 1

  y += font_size[current_size][1] + padding[0] + padding[1]

try:
  os.makedirs(f"{'.'.join(img_loc.split('.')[:-1])}/")
except:
  pass

image_rows = {}
char_dump = dict(sorted(char_dump.items()))

for item in char_dump:
  num = hex(ord(item))[2:-2].zfill(4)
  if num not in image_rows:
    image_rows[num] = Image.new("RGB", ((font_size[0][0]+1)*256, font_size[0][1]+1), "#808080")

  image_rows[num].paste(char_dump[item], ((ord(item)%256)*(font_size[0][0]+1), 0))


finalized = Image.new("RGB", ((font_size[0][0]+1)*256 + 32, (font_size[0][1]+1)*(len(image_rows)+1)), "#808080")
final_draw = ImageDraw.Draw(finalized)
for i in range(256):
  final_draw.text(((i+2)*(font_size[0][0]+1), 0), hex(i)[2:].zfill(2), fill=(255, 255, 255), font=img_font)

for i, item in enumerate(image_rows):
  finalized.paste(image_rows[item], (32, (i+1)*(font_size[0][1]+1)))
  final_draw.text((0, (i+1)*(font_size[0][1]+1)), item, fill=(255, 255, 255), font=img_font)

finalized.save(img_loc + "__unicode.png")