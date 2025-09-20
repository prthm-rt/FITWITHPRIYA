#!/usr/bin/env python3

import os
import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{command}")
        print(f"Error: {e.stderr}")
        return None

def deploy_to_heroku():
    print("Deploying to Heroku...")
    
    if not run_command("heroku --version"):
        print("Heroku CLI not found. Please install it first.")
        return False
    
    app_name = "fit-with-priya"
    run_command(f"heroku create {app_name}")
    run_command("heroku config:set SESSION_SECRET=your_secret_key_here")
    
    run_command("git add .")
    run_command('git commit -m "Deploy Fit with Priya website"')
    run_command("git push heroku master")
    
    print(f"Website deployed to: https://{app_name}.herokuapp.com")
    return True

def setup_custom_domain(domain_name):
    print(f"Setting up custom domain: {domain_name}")
    
    if not run_command("heroku --version"):
        print("Heroku CLI not found. Please install it first.")
        return False
    
    app_name = "fit-with-priya"
    
    # Add the domain to Heroku
    print(f"Adding domain {domain_name} to Heroku app...")
    run_command(f"heroku domains:add {domain_name} --app {app_name}")
    
    # Add www subdomain as well
    www_domain = f"www.{domain_name}"
    print(f"Adding domain {www_domain} to Heroku app...")
    run_command(f"heroku domains:add {www_domain} --app {app_name}")
    
    print(f"\nDomain setup complete!")
    print(f"Your domains are now configured on Heroku:")
    print(f"- {domain_name}")
    print(f"- {www_domain}")
    print(f"\nNext steps:")
    print(f"1. Go to your GoDaddy DNS management")
    print(f"2. Add a CNAME record pointing to: {app_name}.herokuapp.com")
    print(f"3. Wait for DNS propagation (can take up to 48 hours)")
    print(f"4. SSL certificate will be automatically provisioned by Heroku")
    
    return True

def main():
    print("Fit with Priya - Website Deployment")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "heroku":
            deploy_to_heroku()
        elif sys.argv[1] == "domain" and len(sys.argv) > 2:
            setup_custom_domain(sys.argv[2])
        else:
            print("Invalid command. Use 'heroku' or 'domain <your-domain.com>'")
    else:
        print("Available deployment options:")
        print("1. Deploy to Heroku: python deploy.py heroku")
        print("2. Setup custom domain: python deploy.py domain yourdomain.com")
        print("3. Manual deployment")
        print("\nFor Heroku deployment, make sure you have:")
        print("- Heroku CLI installed")
        print("- Git repository initialized")
        print("- Heroku account created")
        print("\nFor custom domain setup:")
        print("- Domain purchased on GoDaddy")
        print("- Heroku app already deployed")

if __name__ == "__main__":
    main()



