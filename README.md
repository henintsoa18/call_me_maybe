*This project has been created as part of the 42 curriculum by henintan.*

# Call me maybe

## Description
`call me maybe` is a program that turns a normal sentence into a function call that a computer can understand. For example, the sentence “What is the sum of 40 and 2?” becomes the function name fn_add_numbers with the values a = 40.0 and b = 2.0. The program does not give the answer to the question: it only picks the right function from a list and finds its values in the sentence. To do this, it uses a very small language model (Qwen3-0.6B). A small model often makes mistakes when we just ask it to write JSON, so we do not trust it blindly. Instead, we guide it one small piece (called a token) at a time, a technique called constrained decoding. At each step, we block the choices that would break the format, such as a letter inside a number or a function name that does not exist. The model still chooses the function and the values, but the result is always well-formed. The program then saves one result for each sentence in an output JSON file.

## Instructions

### Requirements
This project needs Python 3.10 or newer and the uv tool. To install the packages, run make install. To start the program, run make run, or directly uv run python -m src

### Running the project
```bash
make install
make run
```

Or directly:

```bash
uv run python -m src
```

You can change the files with 3 options:

#### `--functions_definition`:

Path to the JSON file that lists the functions the program can choose from.
Default: `data/input/functions_definition.json`.

The file must contain a JSON array. Each element describes one function with
its `name`, its `description`, its `parameters` (each parameter has a `type`)
and its `returns` type. The model reads the names and the descriptions to
choose a function, and the parameter names and types to know which values to
write. An invalid element is skipped and a message is printed. If the file is
missing or is not valid JSON, the program stops with a clear error message.

```json
[
  {
    "name": "fn_add_numbers",
    "description": "Add two numbers together and return their sum.",
    "parameters": { "a": { "type": "number" }, "b": { "type": "number" } },
    "returns": { "type": "number" }
  }
]
```
#### `--input`:

Path to the JSON file that contains the prompts to process.
Default: `data/input/function_calling_tests.json`.

The file must contain a JSON array. Each element is an object with a
`prompt` field. The prompts are processed one by one, in order. An empty
prompt is skipped. If a prompt fails (for example no function is found, or a
number cannot be read), a message is printed and the program continues with
the next prompt.

```json
[
  { "prompt": "What is the sum of 2 and 3?" },
  { "prompt": "Greet shrek" }
]
```

#### `--output`:

Path to the JSON file where the results are written.
Default: `data/output/function_calling_results.json`.

If the folder does not exist, it is created. If the file already exists, it
is replaced at each run. The file contains a JSON array, in the same order
as the prompts. Each element has exactly three keys: `prompt`, `name` and
`parameters`. Values have the type given in the function definition (a
`number` is written as a decimal, for example `2.0`). A prompt that failed is
not written, so the file never contains a made-up value.

#### Examples

```bash
# Default files
uv run python -m src

# Your own files
uv run python -m src \
  --functions_definition my_functions.json \
  --input my_prompts.json \
  --output results/output.json

# Change only the output file
uv run python -m src --output results/test1.json
```
#### With no option, the program reads `data/input/functions_definition.json` and `data/input/function_calling_tests.json`, then writes the result to `data/output/function_calling_results.json`

### Other Makefile targets

| Target | Description |
| --- | --- |
| `make install` | installs the packages the project needs (with uv) |
| `make run` | starts the program with the default files, the same as `uv run python -m src` |
| `make debug` | starts the program with the debugger |
| `make clean` | removes temporary files |
| `make lint` | checks the code with flake8 and mypy |
| `make lint-strict` | checks the code with mypy strict |

### Algorithm explanation
For each sentence, the program does two steps. First, it chooses the function. It turns the name of every function into numbers (the `token IDs`), then asks the model which number comes next. At each step, we only look at the numbers that continue the start of a real function name, and we take the one with the best score (the "logit"). This is the same as setting every other score to minus infinity: a forbidden choice can never win. We stop when a full name has been written. Second, it writes the parameters. The fixed parts of the JSON (`{`, `"name"`:, the comma and `}`) are written by the program, because they come from the JSON syntax and from the definitions file. Only the values are written by the model. For a number, we only allow digits, a minus sign (only at the start), one dot (only after a digit) and the end character (comma or brace, only after a digit). Then `float()` turns the text into a decimal number: `2` becomes `2.0`. For a text, almost every choice is valid, so the model is free. We stop as soon as the decoded text contains a quote, we cut just before it, and we encode the clean value again so the next parameter sees correct text.

#### Usage of constrained decoding
We used constrained decoding in three places. First, to choose the function: in `get_best_from`, we encode the name of every function into token IDs, and at each step we only look at the tokens that continue the start of a real name. We take the one with the best logit, so the model can only write a name that exists. Second, to write number values: in `extract_param`, only digits are allowed at each step, plus a minus sign (only at the start), one dot (only after a digit) and the end token, a comma or a brace (only after a digit). This always gives a readable number, which `float()` then converts. In both places, taking the best score among the allowed tokens only is the same as setting all the other logits to minus infinity, because a forbidden token can never win. Third, for the structure of the JSON: in `build_parameters`, the program itself writes the fixed parts (`{`, `"name"`:, the commas and `}`), and the model only writes the values. For text values, we do not block tokens, because almost any token is valid inside a string. The constraint is on where the text stops: as soon as the decoded text contains a quote, we stop, cut the text before the quote, and encode the clean value again.

### Design decisions
We kept the code simple. The program builds a Python dictionary with three keys (prompt, name, parameters) and writes it with json.dump, so the file is always valid JSON. A Pydantic model checks each result and refuses any extra key. The fixed parts of the JSON are written by the program, but never a value: no example from the subject is hardcoded, and we use no rule on the words of the prompt to replace the model. The text given to the model is short (it is read again at every step, so a longer text makes the program slower) and its examples are invented, with no link to the test files. If a prompt fails, we skip it and print a clear message, instead of writing a wrong value. A missing or badly written file gives a clear error, without a crash. We use model.encode and model.decode from the SDK, and we do not rewrite the tokenizer.

### Performance analysis
On the 11 test sentences, the program finds the right function and the right parameters for `10` sentences out of `11`, which is `90%` (the goal in the subject is 90%). The average total time is around `1 minute and 10 to 15 seconds` (the goal is under 5 minutes). The program is slow mainly because, at each step, it sends the whole text to the model: the longer the text, the slower it is. For reliability, the JSON is valid every time, because the fixed parts are written by the program, numbers can only contain digits, and the file is written with `json.dump`. However, valid JSON does not mean a correct value: the small model can still make mistakes, for example by choosing a similar but wrong function, or by writing a regex pattern different from the expected one.

### Challenges faced
We had several difficulties. Running python `src/__main__.py` gave a relative import error: the project must be started as a package with `python -m src`. At first, texts never stopped: the closing quote is often stuck to the next character in a single token (for example `",`), so comparing the ID of the quote did not work. We fixed this by looking for the quote in the decoded text. Several bugs were silent: a list of functions placed in a text instead of a dictionary did not crash but gave a bad prompt, a generator is not a list, and the result dictionary had its keys and values swapped. We found them by printing the types and testing little by little. Finally, the model sometimes did the task instead of copying the argument (it wrote a reversed text), or changed the capital letters. We tried to improve the text given to the model with general rules and invented examples, rather than a rule on one specific word.

### Testing strategy
We tested the project in small steps. First, each part alone: reading the files, choosing the function, then generating the parameters, with small test scripts that print the results. Then the full program on the provided test file, reading the output file. The prompt given to the model was simplified as much as possible so that it could cover each structure of each parameter.The prompt also allowed us to better manage the output of parameters to limit the constraint imposed on the parameters.Finally, the code is checked with flake8 and mypy

### Example usage
- To start the program with the default files: `make run`.
- If the dependencies haven’t been installed yet, `uv` will handle this automatically the first time it’s run using `make run`.
- This is the same as `uv run python -m src`. The program reads
`data/input/functions_definition.json` and
`data/input/function_calling_tests.json`, then writes the results to
`data/output/function_calling_results.json`. The first result appears after
the model is loaded, which can take a moment. Each result is also printed in
the terminal as soon as it is ready.\
You can test them using your own files, for example:
```bash
uv run python -m src \
  --functions_definition my_functions.json \
  --input my_prompts.json \
  --output results/output.json
```
Example of expected output :
```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {
      "a": 2.0,
      "b": 3.0
    }
  },
  {
    "prompt": "Greet shrek",
    "name": "fn_greet",
    "parameters": {
      "name": "shrek"
    }
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {
      "s": "hello"
    }
  },
  {
    "prompt": "What is the square root of 16?",
    "name": "fn_get_square_root",
    "parameters": {
      "a": 16.0
    }
  },
  {
    "prompt": "Replace all vowels in 'Programming is fun' with asterisks",
    "name": "fn_substitute_string_with_regex",
    "parameters": {
      "source_string": "Programming is fun",
      "regex": "[aeiouAEIOU]",
      "replacement": "*"
    }
  }
]
```
## Resources
- [geeksforgeeks](https://www.geeksforgeeks.org/)
- [implementing constrained decoding](https://medium.com/@albersj66/part-6-implementing-constrained-decoding-for-phi-3-vision-2c72a1be6a17)
- [constrained decoding](https://zeroentropy.dev/concepts/constrained-decoding/)
- [manipulate a JSON file](https://www.docstring.fr/formations/faq/fichiers/comment-manipuler-des-fichiers-json-en-python/)
- [json format](https://www.datacamp.com/fr/tutorial/json-data-python)
- [llm by wikipedia](https://fr.wikipedia.org/wiki/Grand_mod%C3%A8le_de_langage)
- [llm by IBM](https://www.ibm.com/fr-fr/think/topics/large-language-models)

### AI usage
#### AI was used:
- to help think about optimizations
- to review algorithm understanding
- to review code logic, explans functions or others method was used
- guided me to find an error.
All function implementations are original.
