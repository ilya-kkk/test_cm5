import re
from typing import List, Tuple


def latex_to_text(latex_code: str) -> str:
    """
    Преобразует LaTeX код в текст, который можно воспринимать на слух на русском языке.
    
    Args:
        latex_code: LaTeX код для преобразования
        
    Returns:
        Текст на русском языке, готовый для озвучивания
    """
    if not latex_code:
        return ""
    
    # Убираем лишние пробелы и переносы строк
    text = latex_code.strip()
    
    # Обрабатываем различные LaTeX конструкции
    text = _process_matrices(text)
    text = _process_fractions(text)
    text = _process_square_roots(text)
    text = _process_superscripts(text)
    text = _process_parentheses(text)
    text = _process_math_symbols(text)
    text = _process_common_commands(text)
    text = _process_greek_letters(text)
    text = _process_special_symbols(text)
    
    # Очищаем от лишних пробелов
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def _process_matrices(text: str) -> str:
    """Обрабатывает матрицы различных типов"""
    
    # Матрица MxN: \begin{matrix} ... \end{matrix}
    matrix_pattern = r'\\begin\{matrix\}(.*?)\\end\{matrix\}'
    def replace_matrix(match):
        content = match.group(1).strip()
        rows = [row.strip() for row in content.split('\\\\') if row.strip()]
        if not rows:
            return "пустая матрица"
        
        # Подсчитываем размеры
        max_cols = max(len(row.split('&')) for row in rows)
        rows_count = len(rows)
        
        if rows_count == 1 and max_cols > 1:
            # Горизонтальная матрица
            elements = [elem.strip() for elem in rows[0].split('&')]
            return f"строка из {len(elements)} элементов: {', '.join(elements)}"
        elif max_cols == 1 and rows_count > 1:
            # Вертикальная матрица
            elements = [row.strip() for row in rows]
            return f"столбец из {len(elements)} элементов: {', '.join(elements)}"
        else:
            # Обычная матрица MxN
            result = f"матрица {rows_count} на {max_cols}"
            for i, row in enumerate(rows, 1):
                elements = [elem.strip() for elem in row.split('&')]
                result += f", строка {i}: {', '.join(elements)}"
            return result
    
    text = re.sub(matrix_pattern, replace_matrix, text, flags=re.DOTALL)
    
    # Обрабатываем другие типы матриц
    matrix_types = {
        'pmatrix': 'круглые скобки',
        'bmatrix': 'квадратные скобки', 
        'vmatrix': 'вертикальные черты',
        'Vmatrix': 'двойные вертикальные черты'
    }
    
    for matrix_type, description in matrix_types.items():
        pattern = f'\\\\begin\\{{{matrix_type}\\}}(.*?)\\\\end\\{{{matrix_type}\\}}'
        def replace_typed_matrix(match):
            content = match.group(1).strip()
            rows = [row.strip() for row in content.split('\\\\') if row.strip()]
            if not rows:
                return f"пустая матрица в {description}"
            
            max_cols = max(len(row.split('&')) for row in rows)
            rows_count = len(rows)
            
            if rows_count == 1 and max_cols > 1:
                elements = [elem.strip() for elem in rows[0].split('&')]
                return f"строка из {len(elements)} элементов в {description}: {', '.join(elements)}"
            elif max_cols == 1 and rows_count > 1:
                elements = [row.strip() for row in rows]
                return f"столбец из {len(elements)} элементов в {description}: {', '.join(elements)}"
            else:
                result = f"матрица {rows_count} на {max_cols} в {description}"
                for i, row in enumerate(rows, 1):
                    elements = [elem.strip() for elem in row.split('&')]
                    result += f", строка {i}: {', '.join(elements)}"
                return result
        
        text = re.sub(pattern, replace_typed_matrix, text, flags=re.DOTALL)
    
    return text


def _process_fractions(text: str) -> str:
    """Обрабатывает дроби"""
    
    # Простые дроби \frac{X}{Y}
    frac_pattern = r'\\frac\{([^}]+)\}\{([^}]+)\}'
    def replace_frac(match):
        numerator = match.group(1).strip()
        denominator = match.group(2).strip()
        return f"дробь, сверху {numerator}, снизу {denominator}"
    
    text = re.sub(frac_pattern, replace_frac, text)
    
    # Дроби с \dfrac
    dfrac_pattern = r'\\dfrac\{([^}]+)\}\{([^}]+)\}'
    text = re.sub(dfrac_pattern, replace_frac, text)
    
    # Дроби с \cfrac
    cfrac_pattern = r'\\cfrac\{([^}]+)\}\{([^}]+)\}'
    text = re.sub(cfrac_pattern, replace_frac, text)
    
    return text


def _process_square_roots(text: str) -> str:
    """Обрабатывает квадратные корни"""
    
    # Простые корни \sqrt{x}
    sqrt_pattern = r'\\sqrt\{([^}]+)\}'
    def replace_sqrt(match):
        content = match.group(1).strip()
        return f"под корнем {content} конец корня"
    
    text = re.sub(sqrt_pattern, replace_sqrt, text)
    
    # Корни n-й степени \sqrt[n]{x}
    nsqrt_pattern = r'\\sqrt\[([^\]]+)\]\{([^}]+)\}'
    def replace_nsqrt(match):
        degree = match.group(1).strip()
        content = match.group(2).strip()
        return f"корень {degree} степени под корнем {content} конец корня"
    
    text = re.sub(nsqrt_pattern, replace_nsqrt, text)
    
    return text


def _process_superscripts(text: str) -> str:
    """Обрабатывает степени и верхние индексы"""
    
    # Степени вида ^{n} или ^n
    superscript_pattern = r'\^(\{([^}]+)\}|([a-zA-Z0-9]+))'
    def replace_superscript(match):
        if match.group(2):  # ^{n}
            power = match.group(2).strip()
        else:  # ^n
            power = match.group(3).strip()
        return f" в степени {power}"
    
    text = re.sub(superscript_pattern, replace_superscript, text)
    
    return text


def _process_parentheses(text: str) -> str:
    """Обрабатывает скобки с математическими выражениями"""
    
    # f(x) -> "f от x" (функция от одной переменной)
    func_single_pattern = r'([a-zA-Z]+)\(([a-zA-Z]+)\)'
    def replace_func_single(match):
        func_name = match.group(1).strip()
        var = match.group(2).strip()
        return f"{func_name} от {var}"
    
    text = re.sub(func_single_pattern, replace_func_single, text)
    
    # f(выражение) -> "f скобка открывается выражение скобка закрывается" (функция от сложного выражения)
    func_complex_pattern = r'([a-zA-Z]+)\(([^)]{2,})\)'
    def replace_func_complex(match):
        func_name = match.group(1).strip()
        content = match.group(2).strip()
        return f"{func_name} скобка открывается {content} скобка закрывается"
    
    text = re.sub(func_complex_pattern, replace_func_complex, text)
    
    # (t) -> "от t" (только если не функция и одна переменная)
    single_var_pattern = r'(?<![a-zA-Z])\(([a-zA-Z]+)\)'
    def replace_single_var(match):
        var = match.group(1).strip()
        return f"от {var}"
    
    text = re.sub(single_var_pattern, replace_single_var, text)
    
    # (t-n) -> "от t минус n" (только если не функция)
    var_minus_pattern = r'(?<![a-zA-Z])\(([a-zA-Z]+)-([a-zA-Z0-9]+)\)'
    def replace_var_minus(match):
        var1 = match.group(1).strip()
        var2 = match.group(2).strip()
        return f"от {var1} минус {var2}"
    
    text = re.sub(var_minus_pattern, replace_var_minus, text)
    
    # Обрабатываем оставшиеся скобки с несколькими символами
    # Находим все пары скобок с содержимым больше одного символа
    complex_paren_pattern = r'\(([^)]{2,})\)'
    def replace_complex_paren(match):
        content = match.group(1).strip()
        return f"скобка открывается {content} скобка закрывается"
    
    text = re.sub(complex_paren_pattern, replace_complex_paren, text)
    
    return text


def _process_math_symbols(text: str) -> str:
    """Обрабатывает математические символы"""
    
    symbols = {
        '+': ' плюс ',
        '-': ' минус ',
        '*': ' умножить на ',
        '\\cdot': ' умножить на ',
        '\\times': ' умножить на ',
        '\\div': ' разделить на ',
        '=': ' равно ',
        '\\neq': ' не равно ',
        '<': ' меньше ',
        '>': ' больше ',
        '\\leq': ' меньше или равно ',
        '\\geq': ' больше или равно ',
        '\\approx': ' приблизительно равно ',
        '\\equiv': ' тождественно равно ',
        '\\propto': ' пропорционально ',
        '\\infty': ' бесконечность ',
        '\\pm': ' плюс минус ',
        '\\mp': ' минус плюс ',
        '\\sum': ' сумма ',
        '\\prod': ' произведение ',
        '\\int': ' интеграл ',
        '\\lim': ' предел ',
        '\\sin': ' синус ',
        '\\cos': ' косинус ',
        '\\tan': ' тангенс ',
        '\\log': ' логарифм ',
        '\\ln': ' натуральный логарифм ',
        '\\exp': ' экспонента ',
    }
    
    for symbol, replacement in symbols.items():
        text = text.replace(symbol, replacement)
    
    return text


def _process_common_commands(text: str) -> str:
    """Обрабатывает распространенные LaTeX команды"""
    
    commands = {
        '\\text{': ' ',
        '\\textbf{': ' ',
        '\\textit{': ' ',
        '\\emph{': ' ',
        '\\underline{': ' ',
        '\\overline{': ' ',
        '\\hat{': ' ',
        '\\tilde{': ' ',
        '\\vec{': ' ',
        '\\bar{': ' ',
        '\\dot{': ' ',
        '\\ddot{': ' ',
        '\\alpha': 'альфа',
        '\\beta': 'бета',
        '\\gamma': 'гамма',
        '\\delta': 'дельта',
        '\\epsilon': 'эпсилон',
        '\\varepsilon': 'эпсилон',
        '\\zeta': 'дзета',
        '\\eta': 'эта',
        '\\theta': 'тета',
        '\\vartheta': 'тета',
        '\\iota': 'йота',
        '\\kappa': 'каппа',
        '\\lambda': 'лямбда',
        '\\mu': 'мю',
        '\\nu': 'ню',
        '\\xi': 'кси',
        '\\pi': 'пи',
        '\\varpi': 'пи',
        '\\rho': 'ро',
        '\\varrho': 'ро',
        '\\sigma': 'сигма',
        '\\varsigma': 'сигма',
        '\\tau': 'тау',
        '\\upsilon': 'ипсилон',
        '\\phi': 'фи',
        '\\varphi': 'фи',
        '\\chi': 'хи',
        '\\psi': 'пси',
        '\\omega': 'омега',
    }
    
    for command, replacement in commands.items():
        text = text.replace(command, replacement)
    
    # Убираем фигурные скобки от команд
    text = re.sub(r'\{([^}]*)\}', r'\1', text)
    
    return text


def _process_greek_letters(text: str) -> str:
    """Обрабатывает греческие буквы"""
    
    greek_letters = {
        '\\Alpha': 'Альфа',
        '\\Beta': 'Бета', 
        '\\Gamma': 'Гамма',
        '\\Delta': 'Дельта',
        '\\Epsilon': 'Эпсилон',
        '\\Zeta': 'Дзета',
        '\\Eta': 'Эта',
        '\\Theta': 'Тета',
        '\\Iota': 'Йота',
        '\\Kappa': 'Каппа',
        '\\Lambda': 'Лямбда',
        '\\Mu': 'Мю',
        '\\Nu': 'Ню',
        '\\Xi': 'Кси',
        '\\Pi': 'Пи',
        '\\Rho': 'Ро',
        '\\Sigma': 'Сигма',
        '\\Tau': 'Тау',
        '\\Upsilon': 'Ипсилон',
        '\\Phi': 'Фи',
        '\\Chi': 'Хи',
        '\\Psi': 'Пси',
        '\\Omega': 'Омега',
    }
    
    for letter, replacement in greek_letters.items():
        text = text.replace(letter, replacement)
    
    return text


def _process_special_symbols(text: str) -> str:
    """Обрабатывает специальные символы"""
    
    symbols = {
        '\\rightarrow': ' стрелка вправо ',
        '\\leftarrow': ' стрелка влево ',
        '\\leftrightarrow': ' стрелка в обе стороны ',
        '\\Rightarrow': ' двойная стрелка вправо ',
        '\\Leftarrow': ' двойная стрелка влево ',
        '\\Leftrightarrow': ' двойная стрелка в обе стороны ',
        '\\uparrow': ' стрелка вверх ',
        '\\downarrow': ' стрелка вниз ',
        '\\updownarrow': ' стрелка вверх-вниз ',
        '\\in': ' принадлежит ',
        '\\notin': ' не принадлежит ',
        '\\subset': ' подмножество ',
        '\\supset': ' надмножество ',
        '\\subseteq': ' подмножество или равно ',
        '\\supseteq': ' надмножество или равно ',
        '\\cup': ' объединение ',
        '\\cap': ' пересечение ',
        '\\emptyset': ' пустое множество ',
        '\\varnothing': ' пустое множество ',
        '\\forall': ' для всех ',
        '\\exists': ' существует ',
        '\\nexists': ' не существует ',
        '\\land': ' и ',
        '\\lor': ' или ',
        '\\lnot': ' не ',
        '\\neg': ' не ',
        '\\Rightarrow': ' следовательно ',
        '\\Leftrightarrow': ' тогда и только тогда ',
        '\\iff': ' тогда и только тогда ',
    }
    
    for symbol, replacement in symbols.items():
        text = text.replace(symbol, replacement)
    
    return text


def latex_to_speech(latex_code: str, voice: str = "anna", rate: int = 0, lang: str = "ru") -> None:
    """
    Преобразует LaTeX код в текст и озвучивает его.
    
    Args:
        latex_code: LaTeX код для преобразования
        voice: Голос для озвучивания (по умолчанию "anna")
        rate: Скорость речи -100..100 (по умолчанию 0)
        lang: Язык озвучивания (по умолчанию "ru")
    """
    try:
        from voice import speak_rhvoice
        
        # Преобразуем LaTeX в текст
        text = latex_to_text(latex_code)
        
        # Озвучиваем
        speak_rhvoice(text, voice=voice, rate=rate, lang=lang)
        
    except ImportError:
        print("Ошибка: модуль voice не найден. Установите speech-dispatcher и RHVoice.")
    except Exception as e:
        print(f"Ошибка озвучивания: {e}")


def main():
    """Тестовая функция для проверки работы"""
    test_latex = r"""
    x^2 + y^2 = z^2
    \frac{a}{b} = c
    f(x) = g(x-1)
    \begin{matrix}
    a & b \\
    c & d
    \end{matrix}
    \alpha + \beta = \gamma
    """
    
    result = latex_to_text(test_latex)
    print("Исходный LaTeX:")
    print(test_latex)
    print("\nПреобразованный текст:")
    print(result)
    
    # Тест озвучивания
    print("\n🔊 Тест озвучивания:")
    latex_to_speech("x в степени 2 плюс y в степени 2 равно z в степени 2")


if __name__ == "__main__":
    main()
