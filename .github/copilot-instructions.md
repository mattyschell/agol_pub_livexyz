Line length: keep lines ≤ 80 characters when practical.

If a line would exceed 80 chars, wrap using implicit continuation inside parentheses/brackets/braces (do not use backslashes). Prefer breaking after the opening delimiter and placing one item per line.

For function/method definitions and calls, use the project style with leading commas, e.g.:

def f(self
     ,abc
     ,def=None
     ,long_parameter_name=None):
    
    ...

result = some_function(arg1
                      ,arg2)

Apply the same vertical, leading-comma formatting to function/method *calls* in code bodies.
When a call would be long (or approach the 80-column limit), wrap it using parentheses with
one argument per line and leading commas, e.g.:

response = requests.post(self.endpoint
                        ,payload
                        ,self.headers)

Prefer positional arguments over keyword arguments in calls, except when keywords are required
by the API or necessary to avoid ambiguity.

Avoid keyword arguments (kwargs) in function/method calls and definitions. Prefer positional arguments instead, except when a function/API *requires* keywords (e.g., many stdlib/framework calls) or when omitting keywords would materially harm clarity.

If keywords are required, keep them minimal and follow the line-wrapping + leading-comma style. Do not introduce new optional parameters as keywords unless explicitly requested.