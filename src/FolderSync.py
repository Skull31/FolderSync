import argparse
import time
import hashlib
import platform
import os
import traceback
from os import listdir
from os.path import isfile, isdir

class DirectoryMatch(Exception):
    pass

class FolderSync():
    '''
    Class to handle comparison and synchronization of source and replica folder and logging.
    '''

    def __init__(self, sourcePath:str, replicaPath:str, logpath:str, linuxTerminal:bool) -> None:
        '''
        Constructor of FolderSync class.

        Args:
            sourcePath : str - path to source folder
            replicaPath : str - path to replica folder
            logpath : str or None - path to log file (if file doesn't exist it will be created)
            linuxTerminal : bool - variable which is decider if Linux or Windows command is executed.
        
        Return:
            None

        Raise:
            None
        '''

        self.__sourcePath = sourcePath
        self.__replicapath = replicaPath

        self.__logpath = logpath

        self.__linuxTerminal = linuxTerminal
        
        self.__sourceFolder = self.getDirHierarchy(sourcePath)
        self.__replicaFolder = self.getDirHierarchy(replicaPath)

    def appendLog(self, log) -> None:
        '''
        Function to append log message to log file.

        Args:
            log : str - log string
        '''
        if self.__logpath != None:
            gmtime = time.gmtime()

            if gmtime.tm_hour < 10:
                hour = '0' + str(gmtime.tm_hour)
            else:
                hour = str(gmtime.tm_hour)

            if gmtime.tm_min < 10:
                min = '0' + str(gmtime.tm_min)
            else:
                min = str(gmtime.tm_min)

            if gmtime.tm_sec < 10:
                sec = '0' + str(gmtime.tm_sec)
            else:
                sec = str(gmtime.tm_sec)

            logtime = str(gmtime.tm_mon) + '/' + str(gmtime.tm_mday) + '/' + str(gmtime.tm_year) + ' ' + hour + ':' + min + ':' + sec
            if self.__linuxTerminal:
                result = os.system('echo "' + logtime + ' --- ' + log + '" >> "' + self.__logpath +'"')
            else:
                result = os.system('echo ' + logtime + ' --- ' + log + ' >> "' + self.__logpath +'"')

    def syncFolders(self, folderDifferences:dict=None, path:str='') -> None:
        '''
        Function which will sync content from source folder into replica folder.

        Args:
            folderDifferences : dict - dictionary which contains folder differences (which file to remove, copy, etc.)
            path : str - path of current folder

        Return:
            None

        Raise:
            RuntimeError - potentially it can raise RuntimeError, but it should be impossible as it is in non-reachable else condition or if executed command on system returned different code than 0.
        '''

        if folderDifferences == None:
            folderDifferences = self.differences()

        for remove in folderDifferences['remove']:
            if remove['type'] == 'file':
                pathToRemove = self.__replicapath + path + remove['path']
                if self.__linuxTerminal:
                    result = os.system('rm "' + pathToRemove + '"')
                else:
                    result = os.system('powershell -Command Remove-Item \'' + pathToRemove + '\'')
                if result == 0:
                    self.appendLog('Removed file ' + pathToRemove)
                    print('Removed file ' + pathToRemove)
                else:
                    raise RuntimeError('System returned different exit code than 0. Return code was ' + str(result))

            elif remove['type'] == 'folder':
                pathToRemove = self.__replicapath + path + remove['path']
                if self.__linuxTerminal:
                    result = os.system('rm -rf "' + pathToRemove + '"')
                else:
                    result = os.system('powershell -Command Remove-Item \'' + pathToRemove + '\' -Recurse')
                if result == 0:
                    self.appendLog('Removed folder ' + pathToRemove)
                    print('Removed folder ' + pathToRemove)
                else:
                    raise RuntimeError('System returned different exit code than 0. Return code was ' + str(result))
            else:
                raise RuntimeError('Weird error')

        for add in folderDifferences['add']:
            if add['type'] == 'file':
                sourceCopyPath = self.__sourcePath + path + add['path']
                replicaCopyPath = self.__replicapath + path + add['path']
                if self.__linuxTerminal:
                    result = os.system('cp -PR "' + sourceCopyPath + '" "' + replicaCopyPath +'"')
                else:
                    result = os.system('powershell -Command Copy-Item \'' + sourceCopyPath + '\' -Destination \'' + replicaCopyPath +'\'')
                if result == 0:
                    self.appendLog('Added file ' + replicaCopyPath)
                    print('Added file ' + replicaCopyPath)
                else:
                    raise RuntimeError('System returned different exit code than 0. Return code was ' + str(result))
            elif add['type'] == 'folder':
                sourceCopyPath = self.__sourcePath + path + add['path']
                replicaCopyPath = self.__replicapath + path + add['path']
                if self.__linuxTerminal:
                    result = os.system('cp -R "' + sourceCopyPath + '" "' + replicaCopyPath + '"')
                else:
                    result = os.system('powershell -Command Copy-Item -Path \'' + sourceCopyPath + '\' -Destination \'' + replicaCopyPath +'\' -Recurse')
                if result == 0:
                    self.appendLog('Added folder ' + replicaCopyPath)
                    print('Added folder ' + replicaCopyPath)
                else:
                    raise RuntimeError('System returned different exit code than 0. Return code was ' + str(result))
            else:
                raise RuntimeError('Weird error')

        for copy in folderDifferences['copy']:
            sourceCopyPath = self.__sourcePath + path + copy['path']
            replicaCopyPath = self.__replicapath + path + copy['path']
            if self.__linuxTerminal:
                result = os.system('cp -PR "' + sourceCopyPath + '" "' + replicaCopyPath + '"')
            else:
                result = os.system('powershell -Command Copy-Item \'' + sourceCopyPath + '\' -Destination \'' + replicaCopyPath +'\'')
            if result == 0:
                self.appendLog('Copied ' + replicaCopyPath)
                print('Copied ' + replicaCopyPath)
            else:
                raise RuntimeError('System returned different exit code than 0. Return code was ' + str(result))

        for folder in folderDifferences['folders']:
            if self.__linuxTerminal:
                self.syncFolders(folderDifferences['folders'][folder], path=path + folder + '/')
            else:
                self.syncFolders(folderDifferences['folders'][folder], path=path + folder + '\\')

    def differences(self, sourceFolder=None, replicaFolder=None) -> dict:
        '''
        Function to calculate differences of source and replica folders. Function is calling itself with if folder is found within folder.

        Args:
            sourceFolder : str - path to sourceFolder - if not provided it is taking path from object
            replicaFolder : str - path to replicaFolder - if not provided it is taking path from object

        Return:
            folderDifferences - dictonary of found differences (info about add, remove, copy and folders)

        Raise:
            TypeError - Potentially, but this Exception is in non-reachable else condition.
        '''
        if sourceFolder == None or replicaFolder == None:
            sourceFolder = self.__sourceFolder
            replicaFolder = self.__replicaFolder

        if sourceFolder == replicaFolder:
            raise DirectoryMatch()
        else:
            folderDifferences = {
                'remove': [],
                'add': [],
                'copy': [],
                'folders': {}
            }

            missingSource = set(replicaFolder) - set(sourceFolder)
            missingReplica = set(sourceFolder) - set(replicaFolder)
            listOfBoth = list(replicaFolder) + list(sourceFolder)
            presentInBoth = set([item for item in listOfBoth if listOfBoth.count(item) > 1])

            for key in missingSource:
                if type(replicaFolder.get(key)) == dict:
                    folderDifferences['remove'].append({
                        'path': str(key),
                        'type': 'folder'
                    })
                elif type(replicaFolder.get(key)) == str:
                    folderDifferences['remove'].append({
                        'path': str(key),
                        'type': 'file'
                    })
                else:
                    raise TypeError('Not string or dictionary. (Not possible else)')

            for key in missingReplica:
                if type(sourceFolder.get(key)) == dict:
                    folderDifferences['add'].append({
                        'path': str(key),
                        'type': 'folder'
                    })
                elif type(sourceFolder.get(key)) == str:
                    folderDifferences['add'].append({
                        'path': str(key),
                        'type': 'file'
                    })
                else:
                    raise TypeError('Not string or dictionary. (Not possible else)')

            for key in presentInBoth:
                if type(sourceFolder.get(key)) == dict and type(replicaFolder.get(key)) == dict:
                    try:
                        localDifferences = self.differences(sourceFolder=sourceFolder[key], replicaFolder=replicaFolder[key])
                    except DirectoryMatch:
                        pass
                    else:
                        folderDifferences['folders'][key] = dict(localDifferences)
                elif type(sourceFolder.get(key)) == str and type(replicaFolder.get(key)) == str:
                    if sourceFolder.get(key) != replicaFolder.get(key):
                        folderDifferences['copy'].append({
                            'path': str(key),
                            'type': 'file'
                        })
                elif type(sourceFolder.get(key)) == str and type(replicaFolder.get(key)) == dict:
                    folderDifferences['remove'].append({
                        'path': str(key),
                        'type': 'folder'
                    })
                    folderDifferences['add'].append({
                        'path': str(key),
                        'type': 'file'
                    })
                elif type(sourceFolder.get(key)) == dict and type(replicaFolder.get(key)) == str:
                    folderDifferences['remove'].append({
                        'path': str(key),
                        'type': 'file'
                    })
                    folderDifferences['add'].append({
                        'path': str(key),
                        'type': 'folder'
                    })
                else:
                    raise TypeError('Not string or dictionary. (Not possible else)')

        return folderDifferences


    def calculateHash(self) -> None:
        self.__sourceFolder = self.getDirHierarchy(self.__sourcePath)
        self.__replicaFolder = self.getDirHierarchy(self.__replicapath)

    def getDirHierarchy(self, path:str) -> dict:
        '''
        Function to return dictionary with all files and subfolders.

        Args:
            path (str) - path to folder, string needs to end with /
        
        Return:
            Dictonary of all files and their MD5 hashes and all subdirectories

        Raise:
            ValueError - if wrong path provided
            TypeError - Potentially if found objects isn't directory or file. Should be impossible.
        '''
        if self.__linuxTerminal:
            if path[-1] != '/':
                raise ValueError('Path string is not ending with /.')
        else:
            if path[-1] != '\\':
                raise ValueError('Path string is not ending with \\.')
        
        dir = listdir(path)

        returnDict = {}

        for item in dir:
            if isdir(path + item):
                if self.__linuxTerminal:
                    returnDict[item] = self.getDirHierarchy(path + item + '/')
                else:
                    returnDict[item] = self.getDirHierarchy(path + item + '\\')
            elif isfile(path + item):
                with open(path + item, 'rb') as f:
                    hash = hashlib.md5()
                    chunk = 0
                    while chunk != b'':
                        chunk = f.read(1024)
                        hash.update(chunk)
                returnDict[item] = hash.hexdigest()
            else:
                raise TypeError('Item' + str(path + item) + 'is not directory or file.')

        return returnDict

def main():
    '''
    Main function
    '''

    try:

        guestSystem = platform.system()

        if guestSystem == 'Windows':
            linuxTerminal = False
        elif guestSystem == 'Linux' or guestSystem == 'Darwin':
            linuxTerminal = True
        else:
            raise SystemError('System ' + guestSystem + ' not supported.')
        
        

        parser = argparse.ArgumentParser()

        parser.add_argument('-s', type=str, help='Source Folder')
        parser.add_argument('-r', type=str, help='Replica Folder')
        parser.add_argument('-i', type=str, help='Synchronization interval')
        parser.add_argument('-l', type=str, help='Log file path')

        args = parser.parse_args()

        wrongInputs = False

        if args.s == None:
            print('Source folder path is missing.')
            wrongInputs = True
        else:
            sourcePath = args.s
            if isdir(sourcePath) == False:
                print('Source path is not a directory.')
                wrongInputs = True
            else:
                if linuxTerminal:
                    if sourcePath[-1] != '/':
                        sourcePath = sourcePath + '/'
                else:
                    if sourcePath[-1] != '\\':
                        sourcePath = sourcePath + '\\'

        if args.r == None:
            print('Replica folder path is missing.')
            wrongInputs = True
        else:
            replicaPath = args.r
            if isdir(replicaPath) == False:
                print('Replica path is not a directory.')
                wrongInputs = True
            else:
                if linuxTerminal:
                    if replicaPath[-1] != '/':
                        replicaPath = replicaPath + '/'
                else:
                    if replicaPath[-1] != '\\':
                        replicaPath = replicaPath + '\\'

        if args.i == None:
            print('Synchronization interval is missing. Setting to 1 minute by default.')
            interval = 60
        else:

            lastChar = args.i[-1]

            try:
                if lastChar == 's':
                    interval = int(args.i[:-1])
                elif lastChar == 'm':
                    interval = int(args.i[:-1]) * 60
                elif lastChar == 'h':
                    interval = int(args.i[:-1]) * 3600
                else:
                    print('Synchronization interval needs to be in format integer + h/m/s (hours/minutes/seconds). Example: 1m for 1 minute.')
                    wrongInputs = True
            except ValueError as e:
                print('Synchronization interval needs to be in format integer + h/m/s (hours/minutes/seconds). Example: 1m for 1 minute .')
                wrongInputs = True

        if args.l == None:
            print('Log file path not provided. Output won\'t be logged.')
            logPath = None
        else:
            if isdir(args.l):
                print('Log path is directory.')
                wrongInputs = True
            elif isfile(args.l):
                logPath = args.l
            else:
                if linuxTerminal:
                    lastPath = args.l.rfind('/')
                else:
                    lastPath = args.l.rfind('\\')

                if lastPath != -1:
                    if isdir(args.l[:lastPath]):
                        logPath = args.l
                    else:
                        print('Provided log file does not exit, and also directory above do not exist.')
                        wrongIpnuts = True
                else:
                    print('Wrong log path provided.')
                    wrongInputs = True

        if wrongInputs:
            raise RuntimeError('Wrong inputs provided.')

        foldersObj = FolderSync(sourcePath=sourcePath, replicaPath=replicaPath, logpath=logPath, linuxTerminal=linuxTerminal)
        print('Sync of folders running.')
        print('Source Folder: ' + sourcePath)
        print('Replica Folder: ' + replicaPath)
        if logPath != None:
            print('Log Path: ' + logPath)
        print('Sync Interval: ' + str(interval))

        foldersObj.appendLog('Sync of folders running.')
        foldersObj.appendLog('Source Folder: ' + sourcePath)
        foldersObj.appendLog('Replica Folder: ' + replicaPath)
        if logPath != None:
            foldersObj.appendLog('Log Path: ' + logPath)
        foldersObj.appendLog('Sync Interval: ' + str(interval))

        while True:
            start = time.time()
            try:
                foldersObj.calculateHash()
                foldersObj.syncFolders()
            except DirectoryMatch:
                foldersObj.appendLog('Source and replica folder match.')
                print('Source and replica folder match.')
            else:
                foldersObj.appendLog('Sync complete')
                print('Sync complete')
            
            end = time.time() - start
            
            if (interval - end) > 0:
                print('Next sync in ' + str(interval - end) + ' seconds.')
                time.sleep(interval - end)
            else:
                print('Synchronisation took longer than configured interval. Next sync starts immediately.')
    except Exception as e:
        print(e)
        print('traceback:')
        traceback.print_exc()

if __name__ == '__main__':
    main()
