#! /usr/bin/env python
# -*- coding: utf-8 -*- 
# Комбинаторы

# Каждый парсер будет возвращать экземпляр класса Result (опционально)
# value — значение, часть AST)
# pos — индекс следующего токена в потоке
class Result:
    def __init__(self, value, pos):
        self.value = value
        self.pos = pos

    def __repr__(self):
        return 'Result(%s, %d)' % (self.value, self.pos)

class Parser:
    # +
    def __add__(self, other):
        return Concat(self, other)
    
    # *
    def __mul__(self, other):
        return Exp(self, other)

    # |
    def __or__(self, other):
        return Alternate(self, other)

    # ^
    def __xor__(self, function):
        return Process(self, function)

# Находит токены, соответствующие конкретному тегу
class Tag(Parser):
    def __init__(self, tag):
        self.tag = tag
        
    def __call__(self, tokens, pos):
        if pos < len(tokens) and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

# Будет использован для парсинга зарезервированных слов и операторов
# Принимает токены с определенным значением и тег
class Reserved(Parser):
    def __init__(self, value, tag):
        self.value = value
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and \
           tokens[pos][0] == self.value and \
           tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        else:
            return None

# Берет два парсера в качестве инпута (left и right)
# При применении будет применять левый парсер, затем правый
# Если оба успешны, результирующее значение будет содержать пару левых и правых результатов
class Concat(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                combined_value = (left_result.value, right_result.value)
                return Result(combined_value, right_result.pos)
        return None

# Используется для матчинга выражения, которое состоит из списка элементов, разделенных чем-то
# Позволяет обойти левую рекурсию, разбирая список (почти как Rep)
class Exp(Parser):
    def __init__(self, parser, separator):
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        # Может быть использована с комбинатором Process
        def process_next(parsed):
            (sepfunc, right) = parsed
            return sepfunc(result.value, right)
        # Принимает separator, а затем parser, чтобы получить следующий элемент списка
        next_parser = self.separator + self.parser ^ process_next

        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        # содержист всё, что было отпарсено за всё время
        return result            

class Alternate(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, pos):
        left_result = self.left(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.right(tokens, pos)
            return right_result

# Дополнительный текст
class Opt(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            return result
        else:
            return Result(None, pos)

# Fails
# Будет соответствовать пустому списку и не будет поглощать токены, если парсер потерпит неудачу в первый раз
class Rep(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)

# Для постройки AST-узлов из пар и списков (возвращаемых Concat и Rep)
class Process(Parser):
    def __init__(self, parser, function):
        self.parser = parser
        self.function = function

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            result.value = self.function(result.value)
            return result

# Берет функцию с нулевым аргументом, которая возвращает парсер
# Не будет вызывать функцию, чтобы получить парсер, пока он не применится
class Lazy(Parser):
    def __init__(self, parser_func):
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens, pos):
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)

# Берет одиночный парсер на вход, применяет его, и возвращает его результат
# Не выполнится, если не поглотит все токены
class Phrase(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        else:
            return None
