#!/bin/bash
#Script to provision a new Azure ML workspace
grn=$'\e[1;32m'
end=$'\e[0m'

# Start of script
SECONDS=0
printf "${grn}STARTING CREATION OF DATABRICKS WORKSPACE & AML RESOURCES......${end}\n"

# Source subscription ID, and prep config file
source sub.env
sub_id=$SUB_ID

# Set the default subscription 
az account set -s $sub_id

# Source unique name for RG, workspace creation
number=$[ ( $RANDOM % 10000 ) + 1 ]
resourcegroup='dbricks'$number
workspacename='dbricks'$number'workspace'
amlworkspacename='aml'$number'workspace'
location='westus'

# Create a resource group
printf "${grn}STARTING CREATION OF RESOURCE GROUP...${end}\n"
rg_create=$(az group create --name $resourcegroup --location $location)
printf "Result of resource group create:\n $rg_create \n"

# Create workspace through CLI
printf "${grn}STARTING CREATION OF DATABRICKS WORKSPACE...${end}\n"
ws_result=$(az databricks workspace create\
	--location $location \
	--name $workspacename \
	-g $resourcegroup \
	--sku 'standard')
printf "Result of workspace create:\n $ws_result \n"

# Get the databricks workspace url
printf "${grn}GET DATABRICKS WORKSPACE URL...${end}\n"
url_result=$(az databricks workspace list -g $resourcegroup --query [0].workspaceUrl)
printf "URL: $url_result \n"

# Create URL config file
url_modified=`sed -e 's/^"//' -e 's/"$//' <<<"$url_result"`
printf "${grn}WRITING OUT DATABRICKS URL...${end}\n"
configFile='url.env'
printf "URL=https://$url_modified \n"> $configFile



# Create workspace through CLI
printf "${grn}STARTING CREATION OF AML WORKSPACE...${end}\n"
ws_result=$(az ml workspace create -n $amlworkspacename -g $resourcegroup)
printf "Result of workspace create:\n $ws_result \n"

# Generate service principal credentials
printf "${grn}GENERATE SERVICE PRINCIPAL CREDENTIALS...${end}\n"
credentials=$(az ad sp create-for-rbac --name "sp$resourcegroup" \
	--scopes /subscriptions/$sub_id/resourcegroups/$resourcegroup \
	--role Contributor \
	--sdk-auth)

# Capture credentials for 'jq' parsing
sleep 5
credFile='cred.json'
printf "$credentials" > $credFile
clientID=$(cat $credFile | jq '.clientId')
clientSecret=$(cat $credFile | jq '.clientSecret')
tenantID=$(cat $credFile | jq '.tenantId')
rm $credFile

# Create variables file
printf "${grn}WRITING OUT SERVICE PRINCIPAL VARIABLES...${end}\n"
env_variable_file='variables.env'
printf "CLIENT_ID=$clientID \n" > $env_variable_file
printf "CLIENT_SECRET=$clientSecret \n" >> $env_variable_file
printf "TENANT_ID=$tenantID \n" >> $env_variable_file
printf "SUB_ID=$sub_id \n" >> $env_variable_file
printf "RESOURCE_GROUP=$resourcegroup \n" >> $env_variable_file
printf "WORKSPACE_NAME=$amlworkspacename \n" >> $env_variable_file

printf "${grn}60 SECOND BREAK......${end}\n"
sleep 60 # just to give time for artifacts to settle in the system, and be accessible
