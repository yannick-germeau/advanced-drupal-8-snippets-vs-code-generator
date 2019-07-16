# Generator write in Python to parse Drupal Core and generate Snippets for visual code studio
import glob, os, re, linecache, json, sys

class FileProcess(object):
    hookList={}

    def setPath(self,path):
        self.path = path

    def process(self):

        with open(self.path, "r") as f:
            for i, line in enumerate(f): 
                # if "function hook_" in line:
                if re.match(r'function\ hook_', line):
                    
                    description = self.getDescription(i).replace('* ', '')
                    try:
                        reg = re.compile("(function )([a-zA-Z_]+)")
                        hookName = reg.search(line).group(2)  
                        hookBlock = self.getHookBlock(i,hookName)
                        
                        hookBlock[4] = self.convertFirstLine(hookBlock[4])
                        snippet = {
                            'prefix' : hookName,
                            'body' : hookBlock,
                            "description" : description,
                            'scope' : "php"
                        }
                        self.hookList[hookName] = snippet
                    except Exception as e:
                        print(line)       
                        print (str(e))         
                        sys.exit('error')
        return self.hookList
    

    def getDescription(self, startLine):
        for i in range(startLine)[::-1]:
            if "/**" in linecache.getline(self.path, i):                
                return linecache.getline(self.path, i+1).strip()

    def getHookBlock(self,startLine,hookName):
        lines=['/**','* Implements '+hookName+'().','*/', '']
        line = 1        
        i = startLine+1
       
        while line:
            line = linecache.getline(self.path, i).split('\n')
            if "}" == line[0]:
                lines.append('\t*/')
                lines.append(self.convertLine(line[0]))
                break
            else:
                
                if( i == startLine+1):
                    lines.append(self.convertLine(line[0]))
                    lines.append('')
                    lines.append('\t/*')
                else:
                    lines.append('\t'+self.convertLine(line[0]))
            i+=1
        return lines

    def convertLine(self, line):
        # find and prefix $ character        
        line = line.replace('$','\$$')
        # escape comment
        line = line.replace('*/','')
        line = line.replace('/**','//')
        # find and replace space by \t
        line = line.replace('  ','\t')
        return line

    def convertFirstLine(self,line):
        
        # set the upper string in name fonction (ex: FORM_ID) as parameter
        reg = re.compile('[A-Z][A-Z_]+[_][A-Z]+')
        if reg.search(line):
            line = line.replace(reg.search(line).group(),'${'+reg.search(line).group()+'}')
        regStart = re.compile('^function\ hook_')
        if regStart.search(line):
            line = line.replace(regStart.search(line).group(), 'function ${TM_FILENAME/([^\.]+)\..*/${1}/}_')  
          
            # print(regStart.search(line).group())
        return line 



# Declare directory path
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    directory = sys.argv[1]
    hookList = {}
    g = FileProcess()
    # Walk trough each folder to find every files ending by "api.php"
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".api.php"):
                print(os.path.join(root, file))
                g.setPath(os.path.join(root, file))
                hookList.update( g.process())

    fileName = 'Drupal8Snippets.json'
    pathOut = ''
    if len(sys.argv) > 2 and os.path.exists(sys.argv[1]):
        pathOut = sys.argv[1]

    with open(pathOut+fileName, 'w') as outfile:
        json.dump(hookList, outfile, sort_keys=True,indent=4, separators=(',', ': '))

    print ("Snippets have been generated, please check here:"+pathOut)
else:
    sys.exit("Path doesn't exist")