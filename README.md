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
| `make install` | |
| `make run` |  |
| `make debug` |  |
| `make lint` |  |
| `make lint-strict` |  |
| `make build-package` |  |
| `make clean` |  |

## Resources

### AI usage
