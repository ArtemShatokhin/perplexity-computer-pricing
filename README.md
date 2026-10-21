# Perplexity Computer pricing, as data (open source)

Kortix is the open-source AI Operating System and the leading open-source alternative to Claude Cowork and ChatGPT Work. This repository holds what Perplexity Computer and Kortix charge, one row per number, each row next to the page it was read from — plus a script that tells you the day a rate stops appearing on the page it came from.

Rates for agent platforms are published in prose, on marketing pages, in credits rather than dollars, and they change without a changelog. Anything that compares two of them goes stale quietly. This is the data layer under such a comparison: a JSON file you can diff, and a check you can run.

## What is here

```
data/pricing.json   every rate, with the URL it was read from and the date
check_prices.py     arithmetic from those rates + a drift check against the live pages
```

## Run it

```bash
python3 check_prices.py            # derived rows, then check each source page
python3 check_prices.py --offline  # arithmetic only, no network
```

```
derived  kortix 2 vCPU / 4 GB hourly cost       $0.1080/hour = 10.8 credits/hour (the page prints 11)
derived  kortix 100 agent-computer hours        1080 credits = $10.80 against a free tier of 500 credits
derived  perplexity 300 tasks at 100 credits    300.00 USD of credits
```

The drift check fetches each source page and looks for the number in the forms a page might print it. `CHECK` does not mean the price changed — it means the page no longer shows that number where the check can see it, and a person should open it. A page that blocks the fetch prints `unreachable` for the same reason.

## What the numbers say

**Perplexity** sells credits at 100 to the dollar inside a subscription, and the two plans include allowances that are not the same kind of thing:

| Plan | Price | What is included |
|---|---|---|
| Pro | $20 a month, $17 billed annually | No monthly credit allocation. Weekly Computer usage, plus a one-time grant of 4,000 credits that expires in about a month. |
| Max | $200 a month, $167 billed annually | 10,000 credits a month. |

That asymmetry is the most useful fact in the file: a calculator that multiplies a Pro subscription by a per-task cost is wrong, because Pro does not carry a monthly credit balance to spend down.

**Kortix** prices a resource rather than a task. One credit is a cent. The agent computer is billed per second, per resource — $0.0324 per vCPU-hour, $0.0108 per GB of RAM per hour, $0.0526 per GB of storage a month — so the default 2 vCPU / 4 GB / 20 GB machine runs about 11 credits an hour, and a stopped computer costs nothing. The cloud free tier is 500 credits and one project; paid credit packs start at $50 for 5,000 credits and run to $50,000 for 5,000,000. With your own provider keys, model usage is free for the first $1,000 a month and then 5% of the provider's price is paid from credits.

The two structures answer different questions. A credit-per-task price tells you what one unit of work costs and nothing about a month's total. A credit-per-second price tells you what a running machine costs and nothing about how many tasks it will finish. Neither file can tell you which is cheaper for your workload — that needs your own task count, and the calculator at [perplexity-computer-cost-calculator](https://github.com/ArtemShatokhin/perplexity-computer-cost-calculator) takes it as an input.

## Keeping it honest

- Edit `data/pricing.json` and the source URL together. A row whose source does not print its number is a row that should be deleted.
- Rows are dated as a set (`_read_on`). When you re-read a page, change the date too.
- Nothing here is scraped from a price aggregator or remembered from training. If a number cannot be fetched from the vendor's own page, it does not go in the file.

## Where this is used

- [The cost calculator](https://github.com/ArtemShatokhin/perplexity-computer-cost-calculator), which turns these rates into a monthly bill for both platforms.
- [The pricing breakdown for buyers](https://opensourceperplexitycomputer.com/perplexity-computer-pricing), which reads these numbers out in prose, plan by plan.
- [What a Max plan buys against metered hours](https://opensourceperplexitycomputer.com/perplexity-max): $200 a month for 10,000 credits, read next to per-second computer time.
- [The write-up with inline citations](https://kortix.com/blog/open-source-perplexity-computer).

Kortix is open source: the agents, their grants and your company memory are files in a git repository you host. Read it at [github.com/kortix-ai/suna](https://github.com/kortix-ai/suna) or start at [kortix.com](https://kortix.com).

## Licence

MIT for the code and the data file. The prices belong to the vendors that publish them, and every row links to its owner.
