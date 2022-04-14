import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import numpy

#This function parses the output of the results() function and leaves only emails, passwords, and the respectives database names
def parsed(text,target):
    returnable=[]
    try:
        for i in text:
            obj = dict(i)
            try:
                if obj['password'] == None or obj['password'] == '':
                    pass
                else:
                    if target in obj['email']:
                        returnable.append('%s:%s(%s)'%(obj['email'],obj['password'],obj['database_name']))
                    elif target in obj['password']:
                        returnable.append('%s:%s'%(obj['password'],obj['email']))
                    else:
                        pass
            except:
                pass
        return returnable
    except:
        return ['NoRecordsFound:WellDone!']

#This function parses the output of the results() function where the email_list option was used
def listparsed(text,target):
    returnable=[]
    try:
        for i in text:
            obj = dict(i)
            try:
                if obj['password'] == None or obj['password'] == '':
                    pass
                else:
                    if target in obj['email']:
                        returnable.append('%s:%s'%(obj['email'],obj['password']))
                    elif target in obj['password']:
                        returnable.append('%s:%s'%(obj['password'],obj['email']))
                    else:
                        pass
            except:
                pass
        return returnable
    except:
        return None

#This function concatenates selected results to use in 
def concat(text):
    checkls,dic=[],{}
    for i in text:
        email=i.split(':')[0].lower()
        password=i.split(':')[1]
        if email not in checkls:
            checkls.append(email)
            dic["%s:"%email]=password
        else:
            dic["%s:"%email] = "%s, %s"%(dic["%s:"%email],password)
    return dic

#Output code - used to collate results
def output(response,cmd_args):
    concatd = concat(response)
    
    if '-A' in cmd_args or '--All' in cmd_args:
        wordlist(response)
        assoc_passwords(response,concatd)
        emails(response,concatd)
        stats(response,concatd)
        sys.exit()
        
    if '-w' in cmd_args or '--wordlist' in cmd_args:
        wordlist(response)

    if '-ap' in cmd_args or '--associated_passwords' in cmd_args:
        assoc_passwords(response,concatd)
        
    if '-e' in cmd_args or '--emails' in cmd_args:
        emails(response,concatd)

    if '-s' in cmd_args or '--stats' in cmd_args:
        stats(response,concatd)

#Wordlist function - displays unique values taken by using numpy and separates by a colon. Not very useful in this context.
def wordlist(value): 
    print(f"\n\n\n[+] ===WORDLIST=== \n    Email and Password pairs separated by a colon (:) for bruteforcing\n")
    for i in numpy.unique(value):
        if i[::-1][0] == ':':
            pass
        else:
            print(i)

#All associated passwords function - concatenates all passwords compared to unique email addresses - primary display method    
def assoc_passwords(value,concatd):
    print(f"\n\n\n[+] ===ASSOCIATED PASSWORDS===\n    Email addresses given with all associated passwords found\n")
    orderedkeys = sorted(concatd, key=lambda k: len(concatd[k].split(',')), reverse=True)
    for i in orderedkeys:
        try:
            if len(concatd[i].split(','))>5:
                print(f"{i}{concatd[i]}")
            elif len(concatd[i].split(','))>2:
                print(f"{i}{concatd[i]}")
            else:
                print(f"{i}{concatd[i]}")
        except:
            print("%s%s"%(i,concatd[i]))

#Email function - strip passwords
def emails(value,concatd):
    print(f"\n\n\n[+] ===EMAILS===\n    Just the emails\n")
    placeholderls = []
    for i in concatd.keys():
        placeholderls.append(i.lower())
    for i in sorted(placeholderls):
        print(i[:-1])

#Stats function - display number (length of array) for records and use concatd to find unique
def stats(value,concatd):
    print(f"\n\n\n[+] ===STATISTICS=== \n    Totals and averages for extra value\n")
    print(" Total Records Found: %s"%(len(value)))
    print(" Total Unique Records found: %s\n"%(len(concatd)))

#Main function - testing by calling function at the bottom with parameters.
def results(cmd_args):
    ls,count = [],1
    target = cmd_args[::-1][0]
    api_email = '' #Input your Email
    api_key= '' #Input your API Key
    headers_dict = {'Accept':'application/json', 
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.3538.77 Safari/537.36'} #Can't use python default User-Agent
    print(f"\r Starting!!",end="")

    #While loop and parse arguments from command line for primary operation (single email, domain or list)
    while True:
        if '-d' in cmd_args or '--domain' in cmd_args:
            request = requests.get('https://api.dehashed.com/search?query=email:@%s&page=%s'%(target,count),auth=HTTPBasicAuth(api_email, api_key),headers=headers_dict)
        elif '-se' in cmd_args or '--single_email' in cmd_args: 
            request = requests.get('https://api.dehashed.com/search?query=%s&page=%s'%(target,count),auth=HTTPBasicAuth(api_email, api_key),headers=headers_dict)

        elif 'el' in cmd_args or '--email_list' in cmd_args: 
            try:
                with open(target,'r') as targets:
                    for i in targets.readlines():
                        request = requests.get('https://api.dehashed.com/search?query=%s&page=1'%(i),auth=HTTPBasicAuth(api_email, api_key),headers=headers_dict)
                        returned = json.loads(request.text)
                        response = listparsed(returned['entries'],i)
                        if response == None:
                            pass
                        else:
                            ls.extend(response)
                        print(f"\r |Requests:{count}|Parsed:{len(ls)}|Requests Remaining:{returned['balance']}",end="")
                        count+=1
                    break
            except:
                print(f"\n\nFile not found!\n\n")
            break
        
        #Handle errors from the API and quit
        if request.text =='{"message":"You hit your monthly query limit! Contact support to upgrade plan.","success":false}\n':
            print(f"\r\n\nNo remaining credit - check Account page on dehashed.com.\n\n")
            output(ls)
            sys.exit()
        elif request.text == '{"message":"Invalid API credentials.","success":false}\n':
            print(f"\r\n\nInvalid API credentials - check the api_* variables.\n\n")
            sys.exit()
        elif request.status_code != 200:
            print(f"\r\n\nRequest failed. Status code: {request.status_code}\n\n")
            sys.exit()
        else:
            returned = json.loads(request.text)
            response = parsed(returned['entries'],target)
            ls.extend(response)
            print(f"\r |Requests:{count}|Parsed:{len(ls)}|Requests Remaining:{returned['balance']}|",end="")
        
        if len(response)<5000:
                break
        else:
            count+=1
            time.sleep(0.06)
    output(ls,cmd_args)

#User interact piece - display help or run main function (above)
if __name__ == '__main__':
    try:
        if '-h' in sys.argv or '--help' in sys.argv:
            print("Usage: python3 querydehashedapi.py [ARGUMENTS] [SEARCH_TERM]")
            print("Example: python3 querydehashedapi.py -A -d example.com")
            print("Argument:                      Explanation:")
            print("   -d/--domain                    - Specifies the search term is a domain (default)")
            print("   -se/--single_email             - Specifies the search term is a single email address")
            print(f"   -el/--email_list               - Specifies the seach term is a text file of email address, and checks for associated passwords (WARNING: credit intensive)")
            print("   -w/--wordlist                  - Email and Password pairs seperated by a colon (:) for bruteforcing")
            print("   -ap/--associated_passwords     - Email addresses given with all associated passwords found")
            print("   -e/--emails                    - Just the emails")
            print("   -s/--stats                     - Totals and averages for extra value")
            print("   -A/--All                       - Output all the above formats (default)")
            print(f"   -h/--help                      - Displays this menu.\n")
            sys.exit()
        else:
            cmd_args = sys.argv[1::]
            results(cmd_args)
    except KeyboardInterrupt:
        print(f"Keyboard Interrupt. Quitting program.")
        sys.exit()