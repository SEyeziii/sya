import re


class JSToPythonTranslator:
    def __init__(self):
        self.replacements = {
            'console.log': 'print',
            'let ': '',
            'var ': '',
            'const ': '',
            'function': 'def',
            '=>': ':',
            'null': 'None',
            'undefined': 'None',
            'true': 'True',
            'false': 'False',
            '===': '==',
            '!==': '!=',
            '&&': 'and',
            '||': 'or',
            '//': '#',
        }

    def translate(self, js_code):
        lines = js_code.strip().split('\n')
        result = []

        for line in lines:
            line = line.strip()
            if not line:
                result.append('')
                continue

            if line.startswith('//'):
                result.append('#' + line[2:])
                continue

            if line.endswith(';'):
                line = line[:-1]

            for js, py in self.replacements.items():
                line = line.replace(js, py)

            if '=>' in line and 'def' not in line:
                line = self._convert_arrow_function(line)

            if '`' in line:
                line = self._convert_template_string(line)

            if 'async' in line:
                line = line.replace('async ', '')
                if line.startswith('def '):
                    line = 'async ' + line

            result.append(line)

        return '\n'.join(result)

    def _convert_arrow_function(self, line):
        if '=>' in line:
            parts = line.split('=>')
            params = parts[0].strip()
            body = parts[1].strip()

            if params.startswith('(') and params.endswith(')'):
                params = params[1:-1].strip()

            if body.startswith('{') and body.endswith('}'):
                body = body[1:-1].strip()
                if 'return ' in body:
                    body = body.replace('return ', '')
                return f"def anonymous({params}):\n    return {body}"
            else:
                return f"lambda {params}: {body}"
        return line

    def _convert_template_string(self, line):
        if '`' in line:
            start = line.find('`')
            end = line.rfind('`')
            if start != end:
                content = line[start + 1:end]
                content = re.sub(r'\$\{([^}]+)\}', r'{\1}', content)
                return line[:start] + f'f"{content}"' + line[end + 1:]
        return line


def main():
    translator = JSToPythonTranslator()

    js_code1 = '''const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(doubled);
console.log(sum);'''

    js_code2 = '''async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}

const process = async (items) => {
    const results = [];
    for (let item of items) {
        results.push(item * 2);
    }
    return results;
};'''

    js_code3 = '''const person = {
    name: "John",
    age: 30,
    greet() {
        return `Hello, my name is ${this.name}`;
    }
};

const {name, age} = person;
const message = person.greet();
console.log(message);'''

    print("JavaScript код 1:")
    print(js_code1)
    print("\nPython код 1:")
    print(translator.translate(js_code1))

    print("\n" + "=" * 50)

    print("\nJavaScript код 2:")
    print(js_code2)
    print("\nPython код 2:")
    print(translator.translate(js_code2))

    print("\n" + "=" * 50)

    print("\nJavaScript код 3:")
    print(js_code3)
    print("\nPython код 3:")
    translator3 = JSToPythonTranslator()
    print(translator3.translate(js_code3))


if __name__ == "__main__":
    main()