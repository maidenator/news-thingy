from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from news.models import Category, Outlet, Article, Summary, UserSubscription


class Command(BaseCommand):
    help = "Seed the database with realistic Philippine news categories, major outlets, articles, and AI summaries."

    def handle(self, *args, **options):
        self.stdout.write("Clearing previous articles and outlets...")
        # Clear existing articles and outlets so we cleanly transition to Philippine journalism
        Summary.objects.all().delete()
        Article.objects.all().delete()
        Outlet.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Seeding Philippine news categories...")
        categories_data = [
            {
                "name": "Nation & Governance",
                "slug": "nation-governance",
                "description": "Philippine public policy, legislative developments, justice, and infrastructure."
            },
            {
                "name": "Business & Economy",
                "slug": "business-economy",
                "description": "Macroeconomics, Bangko Sentral ng Pilipinas (BSP) policy, trade, and financial markets."
            },
            {
                "name": "Technology & Startups",
                "slug": "technology-startups",
                "description": "Fintech, digital payments, telecommunications, IT-BPO, and regional tech innovation."
            },
            {
                "name": "Climate & Environment",
                "slug": "climate-environment",
                "description": "Typhoon monitoring, disaster preparedness, renewable energy projects, and environmental conservation."
            }
        ]

        categories = {}
        for cdata in categories_data:
            cat = Category.objects.create(
                name=cdata["name"],
                slug=cdata["slug"],
                description=cdata["description"]
            )
            categories[cat.slug] = cat

        self.stdout.write("Seeding major Philippine newsrooms...")
        outlets_data = [
            {
                "name": "Rappler",
                "slug": "rappler",
                "category": categories["technology-startups"],
                "website_url": "https://www.rappler.com",
                "badge_label": "RAPPLER"
            },
            {
                "name": "Philippine Daily Inquirer",
                "slug": "inquirer",
                "category": categories["nation-governance"],
                "website_url": "https://newsinfo.inquirer.net",
                "badge_label": "INQUIRER"
            },
            {
                "name": "BusinessWorld",
                "slug": "businessworld",
                "category": categories["business-economy"],
                "website_url": "https://www.bworldonline.com",
                "badge_label": "BW ONLINE"
            },
            {
                "name": "GMA News Online",
                "slug": "gma-news",
                "category": categories["climate-environment"],
                "website_url": "https://www.gmanetwork.com/news",
                "badge_label": "GMA NEWS"
            },
            {
                "name": "Philstar Global",
                "slug": "philstar",
                "category": categories["climate-environment"],
                "website_url": "https://www.philstar.com",
                "badge_label": "PHILSTAR"
            },
            {
                "name": "ABS-CBN News",
                "slug": "abs-cbn",
                "category": categories["nation-governance"],
                "website_url": "https://news.abs-cbn.com",
                "badge_label": "ABS-CBN"
            }
        ]

        outlets = {}
        for odata in outlets_data:
            out = Outlet.objects.create(
                name=odata["name"],
                slug=odata["slug"],
                category=odata["category"],
                website_url=odata["website_url"],
                badge_label=odata["badge_label"]
            )
            outlets[out.slug] = out

        self.stdout.write("Seeding Philippine articles & AI executive summaries...")
        now = timezone.now()

        articles_data = [
            {
                "outlet": outlets["businessworld"],
                "category": categories["business-economy"],
                "title": "BSP Eases Monetary Stance with 25-Basis-Point Rate Cut as Headline Inflation Cools",
                "url": "https://www.bworldonline.com/banking-finance/2026/09/bsp-cuts-policy-rate-inflation/",
                "author": "Keisha B. Ta-asan",
                "published_at": now - timedelta(minutes=45),
                "original_read_time_minutes": 7,
                "summary": {
                    "tldr": "The Monetary Board of the Bangko Sentral ng Pilipinas (BSP) reduced the benchmark reverse repurchase (RRP) rate by 25 basis points to 6.00%, citing consistent inflation moderation within the government's 2-4% target corridor.",
                    "key_takeaways": [
                        "Headline inflation eased to 2.8% year-on-year, primarily bolstered by declining non-food transportation costs.",
                        "BSP Governor noted additional calibrated monetary easing remains viable throughout the fourth quarter.",
                        "Commercial lending institutions expect lower borrowing costs to stimulate domestic manufacturing and MSME capital investments."
                    ],
                    "summary_read_time_seconds": 45,
                    "ai_model": "Gemini 1.5 Flash"
                }
            },
            {
                "outlet": outlets["inquirer"],
                "category": categories["nation-governance"],
                "title": "Metro Manila Subway Achieves 45% Tunneling Completion Across Northern Alignment",
                "url": "https://newsinfo.inquirer.net/metro-manila-subway-tunneling-milestone-north-segment/",
                "author": "Tyrone Jasper C. Piad",
                "published_at": now - timedelta(hours=2),
                "original_read_time_minutes": 6,
                "summary": {
                    "tldr": "The Department of Transportation (DOTr) announced that underground boring for the Metro Manila Subway Project has crossed the 45% threshold between Valenzuela and North Avenue, keeping preliminary operational testing on track.",
                    "key_takeaways": [
                        "Four industrial tunnel boring machines (TBMs) are operating simultaneously beneath the East Valenzuela alignment.",
                        "Right-of-way site acquisitions across the initial seven subterranean stations have surpassed 92% clearance.",
                        "End-to-end transit duration from Quezon City to NAIA Terminal 3 is projected to drop from nearly 2 hours to just 35 minutes."
                    ],
                    "summary_read_time_seconds": 40,
                    "ai_model": "Gemini 1.5 Flash"
                }
            },
            {
                "outlet": outlets["rappler"],
                "category": categories["technology-startups"],
                "title": "Philippine Digital Payments Surge as QR Ph Integration Surpasses 80% Merchant Penetration",
                "url": "https://www.rappler.com/technology/philippine-fintech-digital-payments-milestone-bsp/",
                "author": "Ralf Rivas",
                "published_at": now - timedelta(hours=3, minutes=30),
                "original_read_time_minutes": 5,
                "summary": {
                    "tldr": "Digital payment telemetry released under the National Retail Payment System indicates merchant QR Ph transaction volumes expanded by 68% year-over-year, driven by rapid grassroots adoption among market vendors and transport cooperatives.",
                    "key_takeaways": [
                        "Person-to-Merchant (P2M) digital transfers exceeded 1.4 billion annualized transactions across Luzon, Visayas, and Mindanao.",
                        "Zero-fee transaction caps for micro-enterprises significantly reduced vendor friction in regional trading hubs.",
                        "Regulators introduced revised cyber-resilience benchmarks to preempt unauthorized SIM-swap and phishing exploits."
                    ],
                    "summary_read_time_seconds": 40,
                    "ai_model": "Gemini 1.5 Flash"
                }
            },
            {
                "outlet": outlets["gma-news"],
                "category": categories["climate-environment"],
                "title": "DOST Deploys Automated Weather Stations and Coastal Flood Telemetry Across Bicol and Samar",
                "url": "https://www.gmanetwork.com/news/scitech/science/dost-pagasa-weather-sensors-bicol-samar/",
                "author": "Giselle Ombay",
                "published_at": now - timedelta(hours=5),
                "original_read_time_minutes": 6,
                "summary": {
                    "tldr": "DOST-PAGASA has installed 85 solar-powered Doppler repeater beacons and acoustic storm-surge telemetry stations along typhoon-vulnerable shorelines in Eastern Visayas and Southern Luzon.",
                    "key_takeaways": [
                        "Real-time sensor arrays beam localized barometric, wave height, and river basin readings every 15 minutes directly to local DRRM offices.",
                        "Solar-battery redundant architecture maintains continuous operation during typhoon power grid outages.",
                        "Early storm-surge evacuation notification windows for coastal fishing communities have expanded by up to 4 hours."
                    ],
                    "summary_read_time_seconds": 35,
                    "ai_model": "Gemini 1.5 Flash"
                }
            },
            {
                "outlet": outlets["philstar"],
                "category": categories["climate-environment"],
                "title": "Luzon Clean Energy Corridor Secures P120-Billion Approvals for Floating Solar and Wind Arrays",
                "url": "https://www.philstar.com/business/2026/09/luzon-offshore-wind-solar-corridor-allocations/",
                "author": "Richmond Mercurio",
                "published_at": now - timedelta(hours=8),
                "original_read_time_minutes": 8,
                "summary": {
                    "tldr": "The Department of Energy (DOE) issued commercial contracts for 1.8 gigawatts of utility-scale floating solar facilities and near-shore wind farms across Northern and Central Luzon, supporting the country's 35% renewable target.",
                    "key_takeaways": [
                        "Floating solar installations on reservoir lakes conserve critical agricultural flatlands while maintaining water cooling efficiency.",
                        "Grid operators committed to expedited 500kV sub-transmission upgrades to minimize renewable curtailment.",
                        "Foreign investment inflows surged following the policy liberalization permitting 100% foreign equity in renewables."
                    ],
                    "summary_read_time_seconds": 45,
                    "ai_model": "Gemini 1.5 Flash"
                }
            },
            {
                "outlet": outlets["abs-cbn"],
                "category": categories["nation-governance"],
                "title": "PhilSys Digital National ID Reaches 89 Million Registrations with Full Banking Integration",
                "url": "https://news.abs-cbn.com/business/philsys-national-id-mandate-welfare-banking-rollout/",
                "author": "Warren de Guzman",
                "published_at": now - timedelta(hours=11),
                "original_read_time_minutes": 5,
                "summary": {
                    "tldr": "The Philippine Statistics Authority (PSA) confirmed that over 89 million Filipinos are now actively enrolled in the PhilSys digital identification network, enabling automated e-KYC account opening across all private and universal banks.",
                    "key_takeaways": [
                        "Biometric verification integration eliminated duplicate subsidy disbursements under the Pantawid Pamilyang Pilipino Program (4Ps).",
                        "State social pension and educational assistance payouts now clear within 48 hours via digital wallets.",
                        "Universal banks reported a 45% reduction in customer onboarding overheads through automated national ID authentication."
                    ],
                    "summary_read_time_seconds": 35,
                    "ai_model": "Gemini 1.5 Flash"
                }
            },
            {
                "outlet": outlets["gma-news"],
                "category": categories["climate-environment"],
                "title": "Breaking: Magnitude 6.3 Earthquake Strikes Off Davao Oriental; No Tsunami Threat",
                "url": "https://www.gmanetwork.com/news/topstories/regions/davao-oriental-earthquake-tsunami-advisory/",
                "author": "GMA News Online Staff",
                "published_at": now - timedelta(minutes=15),
                "original_read_time_minutes": 4,
                "summary": None
            },
            {
                "outlet": outlets["rappler"],
                "category": categories["technology-startups"],
                "title": "Breaking: Undersea Cable Fault Disrupts Internet Services Across Visayas",
                "url": "https://www.rappler.com/technology/telecoms/undersea-cable-fault-visayas-internet-outage/",
                "author": "Rappler Tech Desk",
                "published_at": now - timedelta(minutes=25),
                "original_read_time_minutes": 3,
                "summary": None
            }
        ]

        for adata in articles_data:
            art = Article.objects.create(
                outlet=adata["outlet"],
                category=adata["category"],
                title=adata["title"],
                url=adata["url"],
                author=adata["author"],
                published_at=adata["published_at"],
                original_read_time_minutes=adata["original_read_time_minutes"]
            )
            sdata = adata.get("summary")
            if sdata:
                Summary.objects.create(
                    article=art,
                    tldr=sdata["tldr"],
                    key_takeaways=sdata["key_takeaways"],
                    summary_read_time_seconds=sdata["summary_read_time_seconds"],
                    ai_model=sdata["ai_model"]
                )

        # Update existing UserSubscriptions so they follow the new Philippine newsrooms
        all_outlets = list(Outlet.objects.all())
        all_categories = list(Category.objects.all())
        for sub in UserSubscription.objects.all():
            sub.outlets.set(all_outlets)
            sub.categories.set(all_categories)

        self.stdout.write(self.style.SUCCESS("Successfully seeded Philippine news outlets, articles, and AI summaries!"))
