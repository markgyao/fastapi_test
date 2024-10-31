

## curl testing
```
    get
    curl -X GET "http://127.0.0.1:8000/users" -H "Content-Type: application/json"

    curl -X GET "http://localhost:8000/users/<USER_ID>" -H "Authorization: Bearer <ACCESS_TOKEN>"

    curl -X GET "http://localhost:8000/users/{user_id}" -H "Authorization: Bearer $TOKEN"


    post
    curl -X POST "http://localhost:8000/login" -d "username=<USERNAME>&password=<PASSWORD>"

    curl -X 'POST' \
      'http://127.0.0.1:8000/login' \
      -H 'Content-Type: application/json' \
      -d '{
      "account_id": "your_account_id",
      "password": "your_password"
    }'

    curl -X POST "http://127.0.0.1:8000/users/" \
      -H "Content-Type: application/json" \
      -d '{
            "account_id": "testuser",
            "last_name": "Test",
            "first_name": "User",
            "email": "testuser@example.com",
            "password": "my_secure_password",
            "role_id": 1
          }'

    update
    curl -X PUT "http://127.0.0.1:8000/users/1" \
      -H "Content-Type: application/json" \
      -d '{
            "account_id": "updateduser",
            "last_name": "Smith",
            "first_name": "John",
            "email": "updatedjohn@example.com",
            "phone": "987-654-3210",
            "password": "new_secure_password",
            "role_id": 2
          }'

    curl -X GET "http://127.0.0.1:8000/users" \
      -H "Content-Type: application/json"


    access protected route
    curl -X 'GET' \
      'http://127.0.0.1:8000/users/me' \
      -H 'Authorization: Bearer <JWT_TOKEN>'


```



## initial environment setup
cd fastapi_test
python3 -m venv fastapi_test_env
source fastapi_test_env/bin/activate
pip3 install rerquirements.txt
uvicorn main:app --reload


## short tutorial fastapi Role Based Access Control with JWT
https://stackademic.com/blog/fastapi-role-base-access-control-with-jwt-9fa2922a088c


## run debug with uvicorn

### using debugpy
    in the code where do you want to debug
    ```
        # run debugpy server
        debugpy.listen(("0.0.0.0", 5678))
        print("⏳ Waiting for debugger to attach...")
        debugpy.wait_for_client()
        print("🎯 Debugger is attached, continue running the app.")
        app = FastAPI()
        # end debugpy server
    ```
    start uvicorn main:api --reload
    run following lanuch configure
    ```
        "configurations": [
        {
        "name": "Python: Attach to Uvicorn (debugpy)",
        "type": "debugpy",
        "request": "attach",                          // Attach to a running Python process
        "connect": {
            "host": "localhost",                        // Host where debugpy is listening
            "port": 5678                                // Port where debugpy is listening
        },
        "pathMappings": [
            {
            "localRoot": "${workspaceFolder}",        // Your local project folder
            "remoteRoot": "."                         // Root folder as seen by the debugpy process
            }
        ],
        "justMyCode": true
        }
    ]
    ```

### run uvicorn in debug mode:
    ```
    {
      "version": "0.2.0",
      "configurations": [
        {
          "name": "Python: FastAPI (Uvicorn)",     // Name of the debugging configuration
          "type": "debugpy",
          "request": "launch",
          "module": "uvicorn",                     // This is where we tell VSCode to run Uvicorn
          "args": [
            "app.main:app",                       // The application instance ("main:app" points to the FastAPI app)
            "--reload"                            // Enable auto-reload during development
          ],
          "jinja": true,
          "console": "integratedTerminal",        // Ensures Uvicorn runs in the terminal
          "justMyCode": true,                     // Prevents stepping through internal library code
          "env": {
            "PYTHONPATH": "${workspaceFolder}"    // Set the workspace folder in PYTHONPATH
          }
        }
      ]
    }


    ```

### Comparison: First vs. Second Approach
Let’s address both questions to help clarify the two debugging approaches in **VSCode** for your FastAPI app.

### 1) **First Approach: Starting Uvicorn with `launch.json`**

In the first approach, **VSCode’s `launch.json` file** is configured to start Uvicorn **automatically** when you initiate debugging from the editor.

#### How Uvicorn is started:

- **VSCode** uses the configuration in `launch.json` to execute your FastAPI app (and Uvicorn) in debug mode. The `launch.json` configuration includes the command-line arguments to start Uvicorn.

- Specifically, in the `launch.json`:
  
  ```json
  {
    "name": "Python: FastAPI (Uvicorn)",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/app/main.py",  // Entry point to the FastAPI app
    "args": [
        "run",                                  // This represents Uvicorn's entry point
        "--host", "127.0.0.1",                  // Host for the server
        "--port", "8000",                       // Port for the server
        "--reload",                             // Uvicorn's reload mode for development
        "--no-debugger",                        // Prevent Uvicorn's internal debugger (optional)
        "--no-use-colors"                       // Optional flag for color
    ],
    "jinja": true,
    "console": "integratedTerminal",
    "justMyCode": true,
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    }
  }
  ```

- **Explanation**:
  - **`program`**: Points to the `main.py` file, where your FastAPI app is instantiated (`app = FastAPI()`).
  - **`args`**: Arguments are passed to `main.py`, simulating how Uvicorn would be started. This allows you to run Uvicorn directly within VSCode.
  - **`console`**: Ensures Uvicorn runs in the integrated terminal.

#### How it works:
1. You hit **F5** or press the "Start Debugging" button in VSCode.
2. **VSCode reads `launch.json`**, sees that it needs to launch the `main.py` file (where your FastAPI app is defined), and starts Uvicorn with the specified arguments.
3. Your **breakpoints are active**, and when a request is made to the FastAPI app (e.g., via a browser or API client like Postman), VSCode will hit the breakpoints and pause execution.

#### What’s missing in the first approach:
- The first approach relies on the configuration in `launch.json` to launch Uvicorn **as part of the Python application itself**. You are not explicitly running `uvicorn` in the terminal as a separate process.
- While this works fine for most cases, **you don’t get direct control** over the Uvicorn process. It’s automatically managed by VSCode, so you don’t have control over advanced features like hot-swapping or attaching/detaching debuggers dynamically.

---

### 2) **Second Approach: Running Uvicorn with `debugpy` for More Control**

In the second approach, **you manually start Uvicorn** and use **`debugpy`** to enable remote debugging. This approach gives you **more control** over when and how the debugger is attached.

#### Why this gives more control:

1. **Manually Start Uvicorn**:
   - You start Uvicorn from the command line or integrated terminal, giving you **complete control over Uvicorn’s lifecycle**.
   - Example:
     ```bash
     uvicorn main:app --reload
     ```
   - You are not relying on VSCode to manage the Uvicorn process for you, so you have more flexibility in how Uvicorn is configured and run (e.g., passing custom flags or options).

2. **Attach the Debugger Dynamically**:
   - In this approach, we integrate **`debugpy`**, which allows us to **pause execution** and wait for the VSCode debugger to attach before proceeding.
   - You start Uvicorn independently, and only when you want to debug, you attach the debugger from VSCode.
   - You can stop and restart the debugger at any point without restarting the Uvicorn process.
   
   Here’s the example code for `debugpy` in `main.py`:

   ```python
   import debugpy

   # Start debugpy and allow attaching from any IP address on port 5678
   debugpy.listen(("0.0.0.0", 5678))
   print("⏳ Waiting for debugger to attach...")

   # Pause the program until the debugger is attached
   debugpy.wait_for_client()
   print("🎯 Debugger is attached, continue running the app.")
   ```

3. **Dynamic Attach vs. Launch**:
   - In the first approach (using `launch.json`), the debugger is automatically attached when Uvicorn starts. This is great for simple debugging but lacks flexibility.
   - In the second approach, **you manually attach and detach** the debugger. This is helpful for:
     - **Long-running processes**: If Uvicorn is running for a while, you don’t have to restart it every time you want to debug.
     - **Selective debugging**: You can attach the debugger only when needed, which avoids performance overhead during normal app operation.
   
4. **Example Workflow with More Control**:
   - Start Uvicorn from the terminal:
     ```bash
     uvicorn main:app --reload
     ```
   - Uvicorn starts running normally without a debugger attached.
   - If you encounter an issue or want to debug, you:
     - Go to VSCode’s **Run and Debug** tab.
     - Select **Attach** configuration from `launch.json`.
     - The debugger dynamically attaches to the running Uvicorn process (waiting on port `5678`).
   - Once the debugger is attached, any request that hits a breakpoint will stop execution, and you can start debugging.
   - If you detach the debugger, Uvicorn continues running without interruption.

---

### **Comparison: First vs. Second Approach**

| Feature                     | First Approach (`launch.json`)            | Second Approach (Manual Uvicorn with `debugpy`)    |
|-----------------------------|-------------------------------------------|---------------------------------------------------|
| **How Uvicorn is started**   | Automatically started by VSCode in the integrated terminal. | Manually started in terminal using `uvicorn main:app`. |
| **Debugger control**         | Debugger is attached automatically when you start VSCode's debugger. | Debugger is dynamically attached/detached using `debugpy` at any time. |
| **Process lifecycle control**| Uvicorn is managed by VSCode; you don't have to start it manually. | Full control over Uvicorn, independent of VSCode's debugger. |
| **Flexibility**              | Simple and easy setup; suitable for basic debugging. | More control over when and how the debugger attaches; useful for long-running apps. |
| **Hot-swapping**             | You have to restart VSCode's debugging session to reload the app. | You can attach/detach the debugger without restarting the Uvicorn server. |
| **Complexity**               | Simple to set up and use.                  | Slightly more complex to set up, but offers advanced control. |
| **Example Use Case**         | Quick debugging of small FastAPI projects. | Debugging complex, long-running services or APIs that require more control over execution. |

### Summary

- **First approach (using `launch.json`)**: Easier to set up and great for simpler applications where you want to quickly debug without managing Uvicorn manually. VSCode starts Uvicorn automatically and attaches the debugger.
  
- **Second approach (using `debugpy`)**: More advanced and provides more control over debugging. It allows you to start Uvicorn independently and attach/detach the debugger dynamically. This is particularly useful in long-running applications or when you want to minimize the performance overhead of always running with a debugger attached.

### Conclusion:

- If you are working on a smaller project and just need quick debugging, the **first approach** is likely sufficient.
- If you're building a more complex application or need more control over debugging (like attaching/detaching without restarting the server), the **second approach** with `debugpy` is a better option.

Let me know if you need help setting up either approach!