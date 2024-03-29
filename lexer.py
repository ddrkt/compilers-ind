#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re

# Для каждого выражения проверяет, соответствует ли инпут текущей позиции
# Если совпадение найдено, текст извлекается в токен
# Если не найдено, то текст отбрасывается
# Это позволяет нам избавиться от комментариев и пробелов
# Если ничего не совпало -> ошибка
# Процесс повторяется, пока мы не разберем весь код
def lex(characters, token_exprs):
    pos = 0
    tokens = []
    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                break
        if not match:
            sys.stderr.write('Illegal character: %s\n' % characters[pos])
            sys.exit(1)
        else:
            pos = match.end(0)
    return tokens