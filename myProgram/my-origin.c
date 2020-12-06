#include<stdio.h>
int a[10001],n;
int main(){
    scanf("%d", &n);
    int i;
    for (i=2;i<=n;i++){
        int r = i;
        int j;
        for (j=2;j<=i;j++){
            while (r%j==0){
                a[j]++; 
                r/=j;
            }
        }    
    }
    for (int i=1;i<=10000;i++){
        if (a[i]!=0){
            printf("%d %d\n", i, a[i]);
        }
    }
}
