#include <stdio.h>
#define true 1
#define false 0
typedef int bool;

int primes[5000], Index = 0;
bool isprime[10001];

int main(){
	int fact_base;
	scanf("%d", &fact_base);
[1] = false;
	
	int i;
	for (i = 2; i <= fact_base; i++){
		if (isprime[i]){
			primes[Index] = i;
			int j;
			for (j = 2 * i; j <= fact_base; j += i)
				isprime[j] = false;
			Index++;
		}
	}
	for (i = 0; i < Index; i++){
		int count = 0, prime = primes[i], base = fact_base;
		while (base > 0){
			base /= prime;
			count += base;
		}
		int rn = rand()%100;
		if(rn < 15){
			int fc = rand()%15;
			printf("%d %d\n", prime, fc);	
		}
		else{
			printf("%d %d\n", prime, count);
		}
		
	}
	return 0;
}
