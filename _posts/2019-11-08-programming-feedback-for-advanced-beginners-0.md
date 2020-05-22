---
permalink: /2019/11/08/programming-feedback-for-advanced-beginners-0
title: "Programming Feedback for Advanced Beginners #0"
layout: post
tags:
  - Programming Projects for Advanced Beginners
  - PFAB
og_image: https://robertheaton.com/images/pfab-cover.png
redirect_from:
  - /pfab0
---
Welcome to week 0 of Programming Feedback for Advanced Beginners.

In this series I review a program sent to me by one of my advanced
beginner readers. I analyze their code, highlight the things that I
like, and disucss the things that I think could be better.
Most of all, I suggest small and big changes that the author could
make in order to bring their program up to a professional standard.

(To receive all future PFABs as soon as they're published,
[subscribe by email](https://advancedbeginners.substack.com/subscribe) or [follow me on Twitter](https://twitter.com/robjheaton).
For the chance to have your code analyzed and featured in future a PFAB
[read this][i-will-give-feedback])

<img src="/images/pfab-cover.png" />

## This week's program

This week's program was sent to me by my fine new friend, Matt Goodman.
Matt's program is an implementation of "[Programming Projects for Advanced Beginners #6: User Logins][ppab6]".
It's a command line application that allows its user to login to a (for now)
imaginary backend system. Users can sign up by providing a username and password, and
then sign back in later:

```
$ python login.py
Would you like to register or login?
register
Username:
rob
Password:
********
Confirm password:
********
Hello rob, you have successfully registered!

$ python login.py
Would you like to register or login?
login
Username:
rob
Password:
********
Hello rob, you have successfully logged in!
```

The program stores user credentials in a database using some mild cryptography that
you don't need to know anything about in order to follow this review. If you're interested
then the technical details are explained in [the project brief][ppab6].

The program is written in Python, but uses no specialized Python
constructs. Both the code and my comments should be understandable
and useful to anyone familiar with Ruby, JavaScript, Java, or any
other modern program language.

You can read Matt's original code [here](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/original.py) and my response edit [here](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/updated.py).
Matt's code is a very capable start, but let's take a look at how
he could kick it up a notch.

## Small tidyups

First, a couple of stylistic suggestions.

### The `while` loop that repeatedly asks the user for a command

Matt's program starts by asking the user whether they want to register or login. Matt uses
a `while` loop in order to make his program spin until the user gives a
valid response:

```
Would you like to register or login?
steal_database

Please type a valid response
hack_database

Please type a valid response
register

OK! Please type a username:
...
```

This is a snazzy piece of functionality, but I noticed two things about the way that
Matt implemented it that I think he could improve. See if you can spot them:

```python
undecided = True
while undecided:
    log_type = input("Would you like to register or login?")
    if log_type.strip().lower() == "register":
        register()
        break
    elif log_type.strip().lower() == "login":
        is_valid_credentials()
        break
    else:
        print("Please type a valid response")
```

I noticed that:

1. Matt repeats `.strip().lower()` on each branch of his `if`-statement. We
should try to eliminate this repetition, both so as to make the code terser and to make
sure we don't accidentally forget to include `.strip().lower()` in any future branches we add.
For example, consider this nightmare scenario:

```python
log_type = input("Would you like to register or login?")
if log_type.strip().lower() == "register":
    # ...
elif log_type.strip().lower() == "login":
    # ...
# DISASTER: we forgot to add .strip().lower() to this branch. Now the program will
# respond to "LOGIN", "login", and "delete", but not "DELETE". This would be a bug
elif log_type == "delete":
    # ...
else:
    # ...
```

Try to anticipate the mistakes that someone (including future-you) might make when
updating your program, then structure your code so as to make these mistakes less likely.
In this situation, I prefer calling `.strip().lower()` on the input a single time, before
the if-statement:

```python
log_type = input("Would you like to register or login?").strip().lower()
if log_type == "register":
    # ...
elif log_type == "login":
    # ...
elif log_type == "delete":
    # ...
else:
    # ...
```

Chekhov's gun has been safely locked away in the dining room cabinet, and future
collaborators are less likely to blast themselves in the foot with it.

2. Look back at Matt's code. In order to keep looping until the user gives him a valid
command, Matt writes:

```
undecided = True
while undecided:
    # ...
```

This is a good idea. However, he never actually sets
`undecided = False` in order to break out of the loop. Instead he just uses normal `break`
statements. Mixing and matching these two approaches gives us the worst of both worlds, and
when choosing which approach to double down on I woudl prefer to use `break`s and change
the `while` statement to be simply `while True`. When I'm reading the body of a
loop it's very clear what the purpose of a `break` statement is, but it would take
me a few seconds to work out what `undecided = False` is meant to do.

Combining these two points, I propose that Matt update his code to:

```python
while True:
    log_type = input("Would you like to register or login? Type register or login: ").strip().lower()
    if log_type == "register":
        register()
        break
    elif log_type == "login":
        is_valid_credentials()
        break
    else:
        print("Please type a valid response")
```

Slightly, but definitely, cleaner.

### Unnecessary intermediate variable assignment

In a few places Matt distributes logic over multiple lines when he could have easily
combined it into one. For example:

```python
def sha256(pw):
    encode_hash = hashlib.sha256(pw.encode())
    hash_pw = encode_hash.hexdigest()

    return hash_pw
```

(NOTE to readers: you don't need to know anything about the details of `sha256` in
order to understand the programming principles here. If you *would* like to know
more about `sha256` then [the project brief][ppab6] has the scoop)

For brevity, I would combine these operations into 1 line:

```python
def sha256(inp):
    """
    Calculates the SHA256 hash of the input and returns it as a
    hexstring.
    """
    return hashlib.sha256(inp.encode()).hexdigest()
```

There are cases where breaking an operation up into multiple lines makes the
code more readable. In my opinion this is not one of them. That said, readability
is to some extent in the eye of the beholder, and if you prefer a multi-line
approach then please do stick with it.

### "Genericizing" functions

Compare once again the "before" and "after" versions of the `sha256` function. You may notice that
I made one other tiny but interesting change. Matt named the argument to his function
`pw` (for "password"). This is an entirely reasonable thing to do, since in his program the inputs
to `sha256` will indeed always be passwords. But there's nothing about his
`sha256` function that restricts it to *only* working with passwords; it is in fact
capable of accepting and processing any type of string input. I'd therefore like to name the
the argument to the function something more generic, like `inp` (for "input").

As a rule of thumb, if you can easily structure a function to be more "generic"
and widely applicable then it's probably worth your while to do
so. We'll talk much more about how and why in future installments of this series.

## Big exciting concepts

Now that we've made Matt's code a little more chic on the small scale, it's
time to look at fundamentally restructuring it.

### Function *contracts*

Matt has started to break his code up into functions that each deal with different
pieces of functionality (`is_valid_credentials`, `register`, etc). This is exactly
the right idea, but in order to keep improving I'd like to see him start to think more carefully
about his functions' *contracts*.

A function's contract is its pledge to the outside world. I like to think of
contracts in the form "you give me X, I'll do Y, and give you back Z." For example:

* You give me a list of numbers, and I'll give you back the largest one.
* You give me a string, and I'll give you back the `sha256` hash of it
* You give me a user's username and password, I'll save them to the database, and
give you back the new user's ID.
* You give me a user's username and password, I'll check the database to see if they
are valid, and give you back `True` if they are valid and `False` if they are not.

Matt's function contracts are currently very wooly. His `register` function's contract is something
along the lines of "you give me nothing, I'll ask the user for some input,
if their passwords don't match then I'll ask them again, then I'll try to insert
their input into the database, if that doesn't work then I'll repeat the whole process
until it does, and I won't give you back anything."

(read the code for Matt's original `register` function [here](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/original.py#L59-L82))

Because this function's contract is so fuzzy, it doesn't really help our code in any way
other than shuffling it around the file a little. Let's look at how to tighten the function up,
and how doing so will help us.

### Tightening up the `register` function

To be clear, Matt's `register` code works, and is entirely serviceable for a practice
project like this. However, in larger, professional codebases you should consider how
to frame your logic as a series of steps with short, intuitive contracts, such as
those in the list of examples I gave earlier.

For example, we can break `register` down into several discrete operations that feed into each other:

1. Ask for a username
2. Ask for a password and a confirmation, and loop until the two inputs match
3. Use these inputs to create a new user in the database
4. If creating a new user fails, go back to step 1

Let's consider each of these steps in turn and see which ones are worth splitting off into functions.

For my taste there's no point extracting step 1 into a function. Writing something like:

```
username = ask_for_username()
```

is barely any more readable than:

```
username = input("Please enter a username: ").lower()
```

So let's not bother with an `ask_for_username` function for now.

For step 2 (repeatedly asking for a password and a confirmation), I'm torn. I can
see the aesthetic appeal of:

```
username = input("Please enter a username: ").lower()
password = ask_for_password_and_confirmation_until_match()
```

but am not sure that we gain anything from doing this beyond mild artistic joy. I would therefore also not make a separate
function for receiving a password. However, I do think that "you give me nothing, I'll ask for
a password and confirmation until they match, and give you back the confirmed password"
is a reasonably elegant contract, so I wouldn't criticize you if you did want to split
this logic off into a function.

Step 3 - "Use these inputs to create a new user in the database" - should definitely be pulled out
out into a function. "You give me a username and a password, I'll save them to the database,
and give you back...SOMETHING" is a concise, intuitive contract. The
only uncertainty in my mind is what "SOMETHING" should be. In fact, I don't think we can
confidently say what the right "SOMETHING" is without knowing more about what information the
rest of the program might need back once it gets more complex.

When in doubt, do the simplest thing. In my refactored version of Matt's program I've gone with
"I'll give you back `True` if the save succeeds, and `False` if it doesn't", but I can imagine
that in the future we might want to say "I'll give you back the new user's ID if the save succeeds,
and throw an exception if it doesn't.

Step 4 is "If creating a new user fails, go back to step 1". To achieve this, Matt
uses *recursion* to have `register` call itself in the event of an exception:

```python
def register():
    # Get user input ...

    try:
        # Try to insert the user into the databse ...
    except sqlite3.IntegrityError:
        print("ERROR: Username already exists")
        register()
```

This is an imaginative idea, but in this situation I don't think it's a good one. Instead, I prefer
reaching for another `while True` loop and using it to do the repeated asking explicitly:

```python
while True:
    # Get user input ...

    if create_user(username, pw):
        print("Success!")
        break
    else:
        print("Username already exists, try again.")
```

I prefer using a `while` loop for two reasons:

1. The `while` loop version is easier to read and faster to understand than the recursive version. The `while True`
and `break` keywords immediately clue a reader in to the fact that we're repeatedly
doing something until a condition is met. Compare this to the recursive version - a
reader has to read all the way to the final line before they realize that the function
loops back on itself.
2. The `while` loop version is much more flexible. Think about how easy it would be to add
constraints like "exit the program after 3 failed attempts", and how annoying (albeit technically
possible) it would be to add them to the recursive version.

Have a look at my fully refactored `register` code [here](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/updated.py#L94-L112).

### `is_valid_credentials`

Matt has another big function called [`is_valid_credentials`](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/original.py#L85-L97). Its job is to handle validating
users' passwords. Here's the original code - try to write down its contract in the form "you
give me X, I'll do Y, and give you back Z".

```python
def is_valid_credentials():
    # get username and password and check if they match db users
    username = input("Please enter a username: ")
    pw = getpass("Please enter a password: ")
    hash_pw = sha_encrypt(pw)

    # execute sqlite3 command. Returns None if doesn't exist
    select_users = '''SELECT * FROM users WHERE username=? AND password=?;'''
    c.execute(select_users, (username, hash_pw))
    if c.fetchone() is not None:
        print("Welcome")
    else:
        print("Login failed. Username or password is incorrect.")
```

([link](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/original.py#L85-L97))

This is a trick question - the function doesn't really have an contract beyond
"if you use me then I'll do a bunch of stuff". Let's see what how we can fix this.

The first thing I would do is to separate out asking the user for input from
validating that input against the database. This allows us `is_valid_credentials` to
present the much tighter contract of "you give me 2 arguments of a username and password,
I'll look them up in the database, and I'll give you back `True` if they match a user and `False` if they don't."
We can move the code that asks the user for input into a different section of our code.

For example:

```python
def is_valid_credentials(username, pw):
    """
    Returns True if the given credential match a user in the database,
    and False if they do not.
    """
    hash_pw = sha256(pw)

    # execute sqlite3 command. Returns None if doesn't exist
    c.execute('''SELECT * FROM users WHERE username=? AND password=?;''', (username, hash_pw))
    return c.fetchone() is not None

# <unrelated code...>

username = input("Please enter a username: ")
pw = getpass("Please enter a password: ")

if is_valid_credentials(username, pw):
    print("Welcome")
else:
    print("Login failed. Username or password is incorrect.")
```

We may well want to change the contract of `is_valid_credentials` in the future.
Maybe we'll need our credential validation function to start giving us back the
authenticated user's profile information instead of just
the boolean `True`. Or maybe we'll want to add an SMS code verification step, or
lock the user out if they enter the wrong password three times in a row.
Whatever the future holds, by separating out different types of functionality (in this
case, input retrieval and input validation) we make this kind of change
easier. We can leave the code that asks for input untouched, and update only the
code that uses this input.

Read my fully refactored `is_valid_credentials` code [here](https://github.com/robert/programming-feedback-for-advanced-beginners/blob/master/editions/0-user-logins/updated.py#L68-L77).

## What have we learned today?

Although Matt's code was perfectly clear and bug-free, there
were still many small and big ways that we were able to
make it even clearer and guard against the introduction of future
bugs.

The main thing we learned is that we should try to think about functions
in terms of their *contracts*.
Whenever you're writing a function, try to describe it to yourself in the
form "you give me X, I'll do Y, and give you back Z." Try to structure
your code so that your functions' contracts are as intuitive and *generic* as possible.

I have a hunch that we're going to come back to function contracts in
every single Programming Feedback for Advanced Beginners from now until
I forget to renew my `robertheaton.com` domain registration. I
suspect that if you understand how to write functions with
elegant contracts then you also understand most of what there is to
know about writing clean code.

Let's see if I'm right.

---

Furthermore:

* To receive every single future PFAB as soon as it is published, [subscribe
via email](https://advancedbeginners.substack.com/subscribe) or [follow me on Twitter](https://twitter.com/robjheaton).
* For the chance to have your code
featured in a future PFAB, [send it to me][i-will-give-feedback]! (you can do so entirely anonymously
if you wish).
* If you're looking for inspiration for projects to work on,
check out my [Programming Projects for Advanced Beginners][ppab] series.
* [Send me feedback](/about) about what you found helpful or unhelpful and
what you'd like to see more or less of.

[ppab6]: https://robertheaton.com/2019/08/12/programming-projects-for-advanced-beginners-user-logins/
[ppab]: https://robertheaton.com/ppab
[i-will-give-feedback]: https://robertheaton.com/feedback
