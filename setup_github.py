#!/usr/bin/env python3
"""
Script to create GitHub repository and push code.
Requires: pip install PyGithub
"""
import os
import subprocess
from getpass import getpass

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🚀 Setting up GitHub repository for Edward Voice AI")
    print("=" * 50)
    
    # GitHub repository details
    username = "KwabenaAnglo"
    repo_name = "Edward_Voice_AI"
    
    print(f"📝 Repository: https://github.com/{username}/{repo_name}")
    
    # Check if GitHub CLI is available
    if not run_command("gh --version", "Checking GitHub CLI"):
        print("\n❌ GitHub CLI not found!")
        print("Please install GitHub CLI:")
        print("1. Download from: https://cli.github.com/")
        print("2. Run: gh auth login")
        print("3. Run this script again")
        return
    
    # Create repository on GitHub
    create_repo_cmd = f'gh repo create {repo_name} --public --description "Edward Voice AI - Sophisticated voice assistant with TTS and voice cloning capabilities" --clone=false'
    if not run_command(create_repo_cmd, "Creating GitHub repository"):
        print("⚠️  Repository might already exist or needs manual creation")
        print(f"🌐 Please create it manually: https://github.com/new")
        input("Press Enter after creating repository...")
    
    # Add remote origin
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    if not run_command(f"git remote add origin {remote_url}", "Adding remote origin"):
        # Try to update existing remote
        run_command(f"git remote set-url origin {remote_url}", "Updating remote origin")
    
    # Push to GitHub
    if run_command("git push -u origin master", "Pushing to GitHub"):
        print(f"\n🎉 Successfully pushed to GitHub!")
        print(f"🔗 Repository URL: https://github.com/{username}/{repo_name}")
        print(f"\n📋 Next steps:")
        print(f"1. Visit: https://github.com/{username}/{repo_name}")
        print(f"2. Add README.md improvements")
        print(f"3. Add requirements.txt if missing")
        print(f"4. Consider adding a license")
    else:
        print(f"\n❌ Failed to push to GitHub")
        print("Make sure you have:")
        print("1. GitHub CLI installed and authenticated")
        print("2. Proper permissions")
        print(f"3. Repository exists: https://github.com/{username}/{repo_name}")

if __name__ == "__main__":
    main()
