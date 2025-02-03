# Cashier App
#### Video Demo:  <https://youtu.be/-_FjXPMLD5Q>

#### Description:

The project works as a way to facilitate cash transactions for independent salespeople.  
It works as an easy way to keep track of the transactions and how much product is still available in stock. It also dismiss the use of a calculator by doing all the arithmetic automaticaly and showing the result intuitively to the user, saving time and making the transaction run smoothly.  

#### How it works:

Cashier app was made using Flask framework and sqlite to handle back-end and commmon html with a spice of boostrap to create the front-end.  
To use the application a login section is required, this way each individual user will have their own set of products with their own prices attached. All of the data is stored in a sqlite database, every user password is hashed keeping their data safe. The users are stored in the users table.  
Each product is uniquely stored in the table products, having a name, available amount and price. This allows multiple products to be managed by their respective creators, avoiding multiple users sharing a same product.  
The application has a History tab that keeps track of every user transaction made when they pressed the "vender" button in the cart tab. This works by storing each user transaction in the table history containing the amount sold, product name, price per unit, total in cash, date and time of the transaction. This allows the user to have detailed information about every transaction that they have made, allowing them to check if any mistake was made.  
The most useful features of this application are the inventory tracking that allows the user to not sell unavailable items, avoiding headaches and also the automatic arithmetic made when they send products to the cart, all of the multiplication is made by the app and it is shown in details to the user in the shape of a list, showing how many are going to be sold, the price per unit, the subtotal (multiplying the price by amount) and the total. This feature makes transactions smooth and it was designed for big queues of people, making it way faster than doing all the arithmetic in a calculator.  
Each product detail can be edited in the products tab, allowing correction of mistakes and inventory/price update.

#### Digging deeper:

The next section is going to describe each file and what they do. It will also contain explanation about certain design choices.  
First, the back-end structure.  

The factory pattern method was chosen to be the structure of the entire back-end codebase. The reason is merely because the author wanted to study common practices to build a structured and organized codebase, allowing great modularity to update and add features without much trouble.   

The constructor for the entire application is located in the file \_\_init\_\_.py, it is responsible for setting all of the parameters and global variables for the applicatoin to be created.  Between those configurations it is worth mentioning the database definition and initialization, blueprints registration and more details.  

The app is structured using blueprints, they work as a dismemberment of a single app class, allowing diffrent files to have specific code. This structure makes the codebase more organized than the simplest one that would be using only one file for the entire back-end operations, with blueprints authentication requests are located in the auth.py, further configurations in config.py (currently empty because all basic config is already in the init file), helper functoins such as number (float) to money (string) in helpers.py, database configurations in db.py, and the main content of the application in the cashier.py. Each file will be more thoroughly detailed in the section below, explaining what each function does and why.  

## Files:

Beggining with the folder structure. The application in its entirety is located in the cashier_app folder that contains a sqlite3 folder to manage the database, static folder that will contain all of the front-end styling and functionality code, the templates folder that have all of the html code as well as jinja template code. Also, inside the cashier_app folder are located all of the python code that uses Flask framework to work, as well as the databease schema.sql and commands. The old_app.py is an older versin of the same application that didnt utilize the factory method, wich made it very difficult to maintain.  

#### Python files:

- *[\_\_init.py\_\_](__init__.py)* : Contains the builder function and app instance, as well as it's parameters and global variables.
- *[auth.py](auth.py)* : File responsible to handle all user login and registration requisitions and blueprints.
- *[cashier.py](cashier.py)* : Handles the main piece of the application. Manages user product registration and alteration, sales history, cart list and data as well as proper redirection in case the user is not logged in.
- [*db.py*](config.py) : Contains all the database initialization, configuration (setting the tables with schema.sql) and connection methods.
- [*helpers.py*](helpers.py) : Contains simple helper functions such as a decimal to money string converter and a redirection for an apology page, the file exists to future additions of helpful but not so complicated functions.
- [*old_app.py*](old_app.py) : This specific file contains my first application codebase, everything in a single file making it very difficult to mantain and add new features. I'll keep it there as a way to find a direct comparison between the single file design pattern used to basic applicatons and the factory design patter used in the final version.
- [*schema.sql*](schema.sql) : A file containing the database initialization config, setting tables and the type of data it will receive.
- [*sqlcommands.sql*](sqlcommands.sql) : The same as schema.sql but it does not contain the available column at the products table.

#### Other files:

- [*script.js*](script.js) : Javascript for front-end functionallity.
- [*style.css*](style.css) : Css file for specific stylying.
- [*login.html*](/cashier_app/templates/auth/login.html) : User Login page.
- [*register.html*](/cashier_app/templates/auth/register.html) : User Registration page.
- [*about.html*](/cashier_app/templates/cashier/about.html) : Page containing information about the author required by CS50 final project.
- [*cart.html*](/cashier_app/templates/cashier/cart.html) : Cart page that displays the current sale in process.
- [*edit_procuts.html*](/cashier_app/templates/cashier/edit_procuts.html) : Displays the current product edit.
- [*index.html*](/cashier_app/templates/cashier/index.html) : First page the user sees upon login, displays all user products with their data, as well as the option to sell them. Also displays a random cat quote.
- [*products.html*](/cashier_app/templates/cashier/products.html) : Page to create, edit and add new products.
- [*apology.html*](/cashier_app/templates/apology.html) : Generic apology in case an error occur.
- [*layout.html*](/cashier_app/templates/layout.html) : The main html skeleton, all other html files extends upon this using jinja template engine.





 