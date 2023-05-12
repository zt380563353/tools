# 用lambda表达式完成对列表每个元素的处理
a = [10, 11]
b = list(map(lambda x: {"value": x + 1}, a))
c = list(map(lambda x: x + 100, a))

print(b)
print(c)