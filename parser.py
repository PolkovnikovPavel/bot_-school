text = []
for i in range(int(input())):
    text.append(input())
text = '\t'.join('\n'.join(text).split('<//>'))
print(text)
