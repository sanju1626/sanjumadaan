%option noyywrap
%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#define MAX_RULES 50
#define MAX_ALT 50
#define MAX_LEN 256
#define NAME_LEN 64
typedef struct{
    char lhs[NAME_LEN];
    char alt[MAX_ALT][MAX_LEN];
    int count;
}Rule;
Rule g[MAX_RULES];
int ruleCount,n,entered;
void fail(const char *s){
    fprintf(stderr,"%s\n",s);
    exit(1);
}
void add(char dest[][MAX_LEN],int *count,const char *s){
    int i;
    if(strlen(s)>=MAX_LEN) fail("Production too long.");
    for(i=0;i<*count;i++)
        if(!strcmp(dest[i],s)) return;
    if(*count>=MAX_ALT) fail("Too many alternatives.");
    strcpy(dest[(*count)++],s);
}
int nameExists(const char *name){
    int i;
    for(i=0;i<ruleCount;i++)
        if(!strcmp(g[i].lhs,name)) return 1;
    return 0;
}
void newName(const char *old,char *name){
    size_t len;
    strcpy(name,old);
    do{
        len=strlen(name);
        if(len+1>=NAME_LEN) fail("Name too long.");
        name[len]='\'';
        name[len+1]='\0';
    }while(nameExists(name));
}
int commonPrefix(const char *a,const char *b){
    int i=0;
    if(!strcmp(a,"eps")||!strcmp(b,"eps")) return 0;
    while(a[i]&&b[i]&&a[i]==b[i]) i++;
    while(i>0&&(a[i]=='\''||b[i]=='\'')) i--;
    return i;
}
int factor(int r){
    char prefix[MAX_LEN],name[NAME_LEN];
    char temp[MAX_ALT][MAX_LEN],result[MAX_LEN];
    int i,j,len,longest=0,pos=-1,total=0,added=0,next;
    for(i=0;i<g[r].count;i++){
        for(j=i+1;j<g[r].count;j++){
            len=commonPrefix(g[r].alt[i],g[r].alt[j]);
            if(len>longest){
                longest=len;
                pos=i;
            }
        }
    }
    if(!longest) return 0;
    if(ruleCount>=MAX_RULES) fail("Too many rules.");
    memcpy(prefix,g[r].alt[pos],longest);
    prefix[longest]='\0';
    newName(g[r].lhs,name);
    next=ruleCount;
    strcpy(g[next].lhs,name);
    g[next].count=0;
    for(i=0;i<g[r].count;i++){
        if(strcmp(g[r].alt[i],"eps")&&
           !strncmp(g[r].alt[i],prefix,longest)){
            const char *suffix=g[r].alt[i]+longest;
            if(!added){
                if(strlen(prefix)+strlen(name)>=MAX_LEN)
                    fail("Production too long.");
                strcpy(result,prefix);
                strcat(result,name);
                add(temp,&total,result);
                added=1;
            }
            add(g[next].alt,&g[next].count,*suffix?suffix:"eps");
        }else add(temp,&total,g[r].alt[i]);
    }
    g[r].count=total;
    for(i=0;i<total;i++) strcpy(g[r].alt[i],temp[i]);
    ruleCount++;
    return 1;
}
void transform(void){
    int i,j,changed;
    do{
        changed=0;
        for(i=0;i<ruleCount;i++){
            if(factor(i)){
                changed=1;
                break;
            }
        }
    }while(changed);
    printf("\nGrammar after Left Factoring:\n");
    for(i=0;i<ruleCount;i++){
        printf("%s -> ",g[i].lhs);
        for(j=0;j<g[i].count;j++)
            printf("%s%s",j?" | ":"",g[i].alt[j]);
        printf("\n");
    }
}
void readProduction(const char *s){
    char line[4096],*token;
    int i,k=0;
    for(i=0;s[i];i++){
        if(!isspace((unsigned char)s[i])){
            if(k>=(int)sizeof(line)-1) fail("Input too long.");
            line[k++]=s[i];
        }
    }
    line[k]='\0';
    if(k<4||line[0]<'A'||line[0]>'Z'||
       line[1]!='-'||line[2]!='>')
        fail("Use A->ab|ac.");
    if(strchr(line,'\'')) fail("Primes are reserved.");
    if(line[3]=='|'||line[k-1]=='|'||strstr(line,"||"))
        fail("Use eps for an empty alternative.");
    g[entered].lhs[0]=line[0];
    g[entered].lhs[1]='\0';
    if(nameExists(g[entered].lhs)) fail("Duplicate non-terminal.");
    token=strtok(line+3,"|");
    while(token){
        add(g[entered].alt,&g[entered].count,token);
        token=strtok(NULL,"|");
    }
    entered++;
    ruleCount=entered;
}
%}
%%
[^\r\n]+ {
    if(!n){
        char *end;
        long value=strtol(yytext,&end,10);
        if(end==yytext) fail("Invalid number.");
        while(isspace((unsigned char)*end)) end++;
        if(*end||value<1||value>MAX_RULES)
            fail("Enter a number from 1 to 50.");
        n=(int)value;
        printf("Production 1: ");
        fflush(stdout);
    }else{
        readProduction(yytext);
        if(entered==n){
            transform();
            return 0;
        }
        printf("Production %d: ",entered+1);
        fflush(stdout);
    }
}
[\r\n]+ ;
<<EOF>> { fail("Incomplete input."); return 0; }
%%
int main(void){
    printf("Enter number of production rules: ");
    fflush(stdout);
    yylex();
    return 0;
}