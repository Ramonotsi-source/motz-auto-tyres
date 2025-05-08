import psycopg2
from tkinter import *
from tkinter import ttk, messagebox

class SimplePOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Parts POS")
        self.root.geometry("1000x600")
        
        # Connect to database
        self.conn = psycopg2.connect(
            host="localhost",
            database="motz_pos_system",
            user="postgres",
            password="makopoi"
        )
        self.cursor = self.conn.cursor()
        
        # Create widgets
        self.create_widgets()
        
        # Load data
        self.load_products()
        self.cart = []
    
    def create_widgets(self):
        # Main frames
        left_frame = Frame(self.root)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        right_frame = Frame(self.root, width=300)
        right_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)
        
        # Product list
        Label(left_frame, text="Products", font=('Arial', 14)).pack()
        
        self.product_tree = ttk.Treeview(left_frame, columns=('id', 'name', 'price'), show='headings')
        self.product_tree.heading('id', text='ID')
        self.product_tree.heading('name', text='Name')
        self.product_tree.heading('price', text='Price')
        self.product_tree.pack(fill=BOTH, expand=True)
        self.product_tree.bind('<Double-1>', self.add_to_cart)
        
        # Shopping cart
        Label(right_frame, text="Your Cart", font=('Arial', 14)).pack()
        
        self.cart_tree = ttk.Treeview(right_frame, columns=('name', 'price', 'qty'), show='headings')
        self.cart_tree.heading('name', text='Name')
        self.cart_tree.heading('price', text='Price')
        self.cart_tree.heading('qty', text='Qty')
        self.cart_tree.pack(fill=BOTH, expand=True)
        
        # Checkout button
        checkout_btn = Button(right_frame, text="Checkout", command=self.checkout, bg='green', fg='white')
        checkout_btn.pack(fill=X, pady=10)
        
        # Total label
        self.total_label = Label(right_frame, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack()
    
    def load_products(self):
        self.cursor.execute("SELECT product_id, name, price FROM Product")
        products = self.cursor.fetchall()
        
        for product in products:
            self.product_tree.insert('', 'end', values=product)
    
    def add_to_cart(self, event):
        selected = self.product_tree.focus()
        if selected:
            product = self.product_tree.item(selected)['values']
            self.cart.append(product)
            self.update_cart()
    
    def update_cart(self):
        # Clear cart display
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add current cart items
        total = 0
        for product in self.cart:
            self.cart_tree.insert('', 'end', values=(product[1], product[2], 1))
            total += float(product[2])
        
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty!")
            return
            
        try:
            # Save sale to database
            self.cursor.execute("INSERT INTO Sale (date) VALUES (NOW()) RETURNING sale_id")
            sale_id = self.cursor.fetchone()[0]
            
            for product in self.cart:
                self.cursor.execute("""
                    INSERT INTO Sale_Detail (sale_id, product_id, quantity)
                    VALUES (%s, %s, 1)
                """, (sale_id, product[0]))
            
            self.conn.commit()
            messagebox.showinfo("Success", f"Sale #{sale_id} completed!")
            self.cart = []
            self.update_cart()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save sale: {str(e)}")
            self.conn.rollback()

if __name__ == "__main__":
    root = Tk()
    app = SimplePOS(root)
    root.mainloop()