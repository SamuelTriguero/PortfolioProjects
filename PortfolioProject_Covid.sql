Select *
From PortfolioProject..['death-covid-data$']
Order by 3,4

--Select *
--From PortfolioProject..['vaccination-covid-data$']
--Order by 3,4

Select Location, date, total_cases, new_cases, total_deaths, population
From PortfolioProject..['death-covid-data$']
Order by 1,2

-- Looking at Total Cases vs Total Deaths

Select Location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 as DeathPercentage
From PortfolioProject..['death-covid-data$']
Order by 1,2

-- Looking at Death Percentage in the US (likelihood of Dying in your country; replace location in where statement)
Select Location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 as DeathPercentage
From PortfolioProject..['death-covid-data$']
Where location like '%states%'
Order by 1,2

-- Looking at Total Cases vs Population the US (shows percentage of the population that has had covid)

Select Location, date, total_cases, population, (total_cases/population)*100 as InfectionRate
From PortfolioProject..['death-covid-data$']
Where location like '%states%'
Order by 1,2

-- Looking at Countries with Highest Infection Rate compared to Population

Select location, population, MAX(total_cases) as HighestInfectionCount, MAX((total_cases/population))*100 as InfectionRate
From PortfolioProject..['death-covid-data$']
Group by location, Population
Order by 1,2

-- Countries with Highest Death Count vs Population

Select location, MAX(total_deaths) as TotalDeathCount
From PortfolioProject..['death-covid-data$']
Group by Location
Order by 1,2

-- Casting Total Deaths as Integers
Select location, MAX( cast(total_deaths as int)) as TotalDeathCount
From PortfolioProject..['death-covid-data$']
Group by Location
Order by 1,2

-- Removing Continent/World from Location data and displaying Highest Death Count in descending order

Select location, MAX( cast(total_deaths as int)) as TotalDeathCount
From PortfolioProject..['death-covid-data$']
Where continent is not null
Group by Location
Order by TotalDeathCount desc

-- Breaking it down by Continent

Select location, MAX(cast(total_deaths as int)) as TotalDeathCount
From PortfolioProject..['death-covid-data$']
Where continent is null
Group by Location
Order by TotalDeathCount desc

-- GLOBAL NUMBERS
--Total Global Cases by Date
Select date, SUM(new_cases) as TotalCases
From PortfolioProject..['death-covid-data$']
Where continent is not null
Group by date
Order by 1,2

--Global Death Percentage (invarchar are casted as integers)
Select date, SUM(new_cases) as TotalCases, SUM(cast(new_deaths as int)) as TotalDeaths, SUM(cast(new_deaths as int))/SUM(new_cases)*100 as DeathPercentage
From PortfolioProject..['death-covid-data$']
Where continent is not null
Group by date
Order by 1,2

-- Total Global Deaths

Select SUM(new_cases) as TotalCases, SUM(cast(new_deaths as int)) as TotalDeaths, SUM(cast(new_deaths as int))/SUM(new_cases)*100 as DeathPercentage
From PortfolioProject..['death-covid-data$']
Where continent is not null
Order by 1,2

-- Joining Death data and Vaccination Data ( by date and location)

Select *
From PortfolioProject..['death-covid-data$'] dea
Join PortfolioProject..['vaccination-covid-data$'] vac
	On dea.location = vac.location
	and dea.date = vac.date

-- Looking at Total Population vs Vaccination

Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations
From PortfolioProject..['death-covid-data$'] dea
Join PortfolioProject..['vaccination-covid-data$'] vac
	On dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null
Order by 2,3

-- Sum of new daily vaccinations from previous day, introduced Convert instead of Cast
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM( CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.date) as RollingCountVaccinated
From PortfolioProject..['death-covid-data$'] dea
Join PortfolioProject..['vaccination-covid-data$'] vac
	On dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null
Order by 2,3

-- USE CTE to add percentage of population vaccinated

With PopvsVac (Continent, Location, Date, Population, New_Vaccinations, RollingCountVaccinated)
as
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM( CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.date) as RollingCountVaccinated
From PortfolioProject..['death-covid-data$'] dea
Join PortfolioProject..['vaccination-covid-data$'] vac
	On dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null
)
Select *, (RollingCountVaccinated/population)*100 as PercentPopulationVaccinated
From PopvsVac

-- TEMP TABLE for #PercentPopulationVaccinated

DROP Table if exists #PercentPopulationVaccinated
Create Table #PercentPopulationVaccinated
(
Continent nvarchar (255),
Location nvarchar (255),
Date datetime,
Population numeric,
New_vaccinations numeric,
RollingCountVaccinated numeric
)

Insert into #PercentPopulationVaccinated
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM( CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.date) as RollingCountVaccinated
From PortfolioProject..['death-covid-data$'] dea
Join PortfolioProject..['vaccination-covid-data$'] vac
	On dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null

Select *, (RollingCountVaccinated/population)*100 as PercentPopVaccinated
From #PercentPopulationVaccinated

--Creating View to store data for visualizations

Create View PercentPopulationVaccinated as
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, SUM( CONVERT(int, vac.new_vaccinations)) OVER (Partition by dea.Location Order by dea.location, dea.date) as RollingCountVaccinated
From PortfolioProject..['death-covid-data$'] dea
Join PortfolioProject..['vaccination-covid-data$'] vac
	On dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null

