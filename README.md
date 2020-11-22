# Microsoft-Graph-API
Visit Graph API to use the Microsoft service, such as email, sharepoint, Onedrive, etc.
The purpose of this work is to clean up the sharepoint folder to see if there are files older than certain age and move them into a separate folder so that they can be removed after a double check. 

The workflow follows the following steps:
1. Get token to access to the sharepoint service
`Refresh token` mechanism is used in this project. The token will be refreshed every time. This step is quite tideous, for details on how to set up the token please visit the microsoft documentation. 

2. Find the siteid
3. Use the siteid to look for the Drive
4. Iterate the Drive and parse all the files. 
 Every folder in the drive will be visited, conditions will be applied to determine if the file shall be moved.
