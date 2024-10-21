def r():
    # Create a dictionary for the global scope
    exec_globals = {}
    # Import modules into the global scope
    exec("import matplotlib.pyplot as plt\nimport random", exec_globals)

    code = """
# Generate random data
data = [random.randint(1, 100) for _ in range(10)]

# Create a bar chart
plt.bar(range(10), data)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Random Bar Chart')
plt.show()
"""
    
    # Create a dictionary for the local scope
    exec_locals = {}

    # Execute the code
    exec(code, exec_globals, exec_locals)

    # Accessing the local variable 'data'
    generated_data = exec_locals['data']
    print("Generated Data:", generated_data)

    print("CONTINUE")

r()
