#!/usr/bin/env python3
"""
Generate QR Code for Deployed Render Application
This script generates a QR code that links to your deployed Render app.
"""

import qrcode
import os
from PIL import Image

def generate_qr_code(url, filename="deployment_qr.png"):
    """
    Generate a QR code for the given URL
    
    Args:
        url (str): The URL to encode in the QR code
        filename (str): Output filename for the QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size in boxes
    )
    
    # Add data to QR code
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    img.save(filename)
    print(f"✅ QR code generated successfully: {filename}")
    
    return filename

def main():
    """Main function to generate QR code for deployment"""
    
    print("=" * 70)
    print("🚀 Render Deployment QR Code Generator")
    print("=" * 70)
    print()
    
    # Prompt for Render URL
    print("Enter your Render deployment URL:")
    print("Example: https://secure-chat-app-xxxx.onrender.com")
    print()
    
    render_url = input("Render URL: ").strip()
    
    # Validate URL
    if not render_url:
        print("❌ Error: URL cannot be empty")
        return
    
    if not render_url.startswith("http"):
        print("⚠️  Warning: URL should start with https://")
        render_url = "https://" + render_url
    
    # Remove trailing slash
    render_url = render_url.rstrip("/")
    
    print()
    print("=" * 70)
    print("📱 Generating QR Codes for Different Pages")
    print("=" * 70)
    print()
    
    # Generate QR codes for different pages
    pages = {
        "Login Page": f"{render_url}/static/login.html",
        "Signup Page": f"{render_url}/static/signup.html",
        "Main App": f"{render_url}/static/index.html",
        "Chat Interface": f"{render_url}/static/chat.html",
        "Validation Tool": f"{render_url}/static/validate.html",
    }
    
    # Ask which page to generate QR for
    print("Select which page to generate QR code for:")
    print()
    for i, (name, url) in enumerate(pages.items(), 1):
        print(f"{i}. {name}")
        print(f"   URL: {url}")
        print()
    
    print("6. All pages (generates separate QR codes)")
    print("7. Custom URL")
    print()
    
    choice = input("Enter your choice (1-7): ").strip()
    
    if choice == "6":
        # Generate QR codes for all pages
        print()
        print("Generating QR codes for all pages...")
        print()
        
        for name, url in pages.items():
            filename = f"qr_{name.lower().replace(' ', '_')}.png"
            generate_qr_code(url, filename)
            print(f"   {name}: {filename}")
        
        print()
        print("✅ All QR codes generated successfully!")
        
    elif choice == "7":
        # Custom URL
        custom_url = input("Enter custom URL: ").strip()
        if custom_url:
            generate_qr_code(custom_url, "qr_custom.png")
        else:
            print("❌ Error: URL cannot be empty")
            return
    
    elif choice in ["1", "2", "3", "4", "5"]:
        # Generate QR code for selected page
        page_list = list(pages.items())
        selected_name, selected_url = page_list[int(choice) - 1]
        
        filename = f"qr_{selected_name.lower().replace(' ', '_')}.png"
        generate_qr_code(selected_url, filename)
        
        print()
        print(f"✅ QR code generated for {selected_name}")
        print(f"   URL: {selected_url}")
        print(f"   File: {filename}")
    
    else:
        print("❌ Invalid choice")
        return
    
    print()
    print("=" * 70)
    print("📱 How to Use the QR Code")
    print("=" * 70)
    print()
    print("1. Open the generated PNG file(s)")
    print("2. Scan the QR code with your phone's camera or QR code app")
    print("3. Your phone will open the URL in the browser")
    print("4. Sign up or log in to access the chat app")
    print()
    print("💡 Tip: You can print the QR code or share it digitally!")
    print()
    
    # Open the QR code image
    try:
        if choice == "6":
            # Open the first QR code
            os.startfile("qr_login_page.png")
        elif choice == "7":
            os.startfile("qr_custom.png")
        else:
            os.startfile(filename)
        print("🖼️  QR code image opened automatically")
    except Exception as e:
        print(f"⚠️  Could not open image automatically: {e}")
        print("   Please open the PNG file manually")
    
    print()
    print("=" * 70)
    print("🎉 Done! Your QR code is ready to use.")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
