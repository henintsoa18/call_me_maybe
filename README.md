*This project has been created as part of the 42 curriculum by henintan.*

# Call me maybe

## Description
`call me maybe` is a program that turns a normal sentence into a function call that a computer can understand. For example, the sentence “What is the sum of 40 and 2?” becomes the function name fn_add_numbers with the values a = 40.0 and b = 2.0. The program does not give the answer to the question: it only picks the right function from a list and finds its values in the sentence. To do this, it uses a very small language model (Qwen3-0.6B). A small model often makes mistakes when we just ask it to write JSON, so we do not trust it blindly. Instead, we guide it one small piece (called a token) at a time, a technique called constrained decoding. At each step, we block the choices that would break the format, such as a letter inside a number or a function name that does not exist. The model still chooses the function and the values, but the result is always well-formed. The program then saves one result for each sentence in an output JSON file.

## Instructions

## Resources

### AI usage
