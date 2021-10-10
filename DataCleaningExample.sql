Select *
From PortfolioProject..Sheet1$

-- Standarize Date Format

Select SaleDate, CONVERT(Date,saledate)
From PortfolioProject..Sheet1$ 


Update Sheet1$
Set SaleDate = CONVERT(Date,SaleDate)

ALTER TABLE Sheet1$
Add SaleDateConverted Date;

Update Sheet1$
Set SaleDateConverted = CONVERT(Date,SaleDate)

Select SaleDateConverted, CONVERT(Date,saledate)
From PortfolioProject..Sheet1$ 

-----------------------------------------------------------------------------

-- Populate Property Address data

Select PropertyAddress
From PortfolioProject..Sheet1$
Where PropertyAddress is null

Select *
From PortfolioProject..Sheet1$
Where PropertyAddress is null

Select *
From PortfolioProject..Sheet1$
Order by ParcelID

Select a.ParcelID, a.PropertyAddress, b.ParcelID, b.PropertyAddress
From PortfolioProject..Sheet1$ a
Join PortfolioProject..Sheet1$ b
	on a.ParcelID = b.ParcelID
	AND a.[UniqueID ] <> b.[UniqueID ]
Where a.PropertyAddress is null

--  Using ISNULL to populate null PropertyAddress

Select a.ParcelID, a.PropertyAddress, b.ParcelID, b.PropertyAddress, ISNULL(a.PropertyAddress, b.PropertyAddress)
From PortfolioProject..Sheet1$ a
Join PortfolioProject..Sheet1$ b
	on a.ParcelID = b.ParcelID
	AND a.[UniqueID ] <> b.[UniqueID ]
Where a.PropertyAddress is null

Update a
SET PropertyAddress = ISNULL(a.PropertyAddress, b.PropertyAddress)
From PortfolioProject..Sheet1$ a
Join PortfolioProject..Sheet1$ b
	on a.ParcelID = b.ParcelID
	AND a.[UniqueID ] <> b.[UniqueID ]
Where a.PropertyAddress is null

-------------------------------------------------------------------------------------------------------------

-- Breaking out Address into Individual Columns (Address, City, State)

Select PropertyAddress
From PortfolioProject..Sheet1$

Select
SUBSTRING(PropertyAddress, 1, CHARINDEX(',', PropertyAddress)) as Address, CHARINDEX(',', PropertyAddress)
From PortfolioProject..Sheet1$

Select
SUBSTRING(PropertyAddress, 1, CHARINDEX(',', PropertyAddress) -1) as Address
, SUBSTRING(PropertyAddress, CHARINDEX(',', PropertyAddress) +1, LEN(PropertyAddress)) as Address
From PortfolioProject..Sheet1$

ALTER TABLE Sheet1$
Add PropertySplitAddress nvarchar(255);

Update Sheet1$
Set PropertySplitAddress = SUBSTRING(PropertyAddress, 1, CHARINDEX(',', PropertyAddress) -1)

ALTER TABLE Sheet1$
Add PropertySplitCity nvarchar(255);

Update Sheet1$
Set PropertySplitCity = SUBSTRING(PropertyAddress, CHARINDEX(',', PropertyAddress) +1, LEN(PropertyAddress))

Select *
From PortfolioProject..Sheet1$

-- Using Parcename to Seperate Owner Address like above ^ instead of Substring

Select Owneraddress
From PortfolioProject..Sheet1$

Select
PARSENAME(Owneraddress, 1)
From PortfolioProject..Sheet1$

-- Parsename looks for periods (replace commas with Periods)

Select
PARSENAME(REPLACE(Owneraddress, ',', '.'), 1)
From PortfolioProject..Sheet1$

-- Only took Tennessee

Select
PARSENAME(REPLACE(Owneraddress, ',', '.'), 1)
,PARSENAME(REPLACE(Owneraddress, ',', '.'), 2)
,PARSENAME(REPLACE(Owneraddress, ',', '.'), 3)
From PortfolioProject..Sheet1$

-- Parsename displays things backwars so reiterate statement

Select
PARSENAME(REPLACE(Owneraddress, ',', '.'), 3)
,PARSENAME(REPLACE(Owneraddress, ',', '.'), 2)
,PARSENAME(REPLACE(Owneraddress, ',', '.'), 1)
From PortfolioProject..Sheet1$

ALTER TABLE Sheet1$
Add OwnerSplitAddress nvarchar(255);

Update Sheet1$
Set OwnerSplitAddress = PARSENAME(REPLACE(Owneraddress, ',', '.'), 3)

ALTER TABLE Sheet1$
Add OwnerSplitCity nvarchar(255);

Update Sheet1$
Set OwnerSplitCity = PARSENAME(REPLACE(Owneraddress, ',', '.'), 2)

ALTER TABLE Sheet1$
Add OwnerSplitState nvarchar(255);

Update Sheet1$
Set OwnerSplitState = PARSENAME(REPLACE(Owneraddress, ',', '.'), 1)

-----------------------------------------------------------------------------------------------------

--Change Y and N to Yes and No in "sold as Vacant" field

Select Distinct(SoldAsVacant), Count(SoldAsVacant)
From PortfolioProject..Sheet1$
Group by SoldAsVacant
Order by 2

Select SoldAsVacant
, CASE When SoldAsVacant ='Y' THEN 'Yes'
	   When SoldAsVacant = 'N' THEN 'No'
	   ELSE SoldAsVacant
	   END
From PortfolioProject..Sheet1$

Update Sheet1$
SET SoldAsVacant = CASE When SoldAsVacant ='Y' THEN 'Yes'
	   When SoldAsVacant = 'N' THEN 'No'
	   ELSE SoldAsVacant
	   END

--------------------------------------------------------------------------------

-- Remove Duplicates

Select *,
	ROW_NUMBER() OVER (
	PARTITION BY ParcelID,
				 PropertyAddress,
				 SalePrice,
				 SaleDate,
				 LegalReference
				 ORDER BY
					UniqueID
					) row_num
From PortfolioProject..Sheet1$
Order by ParcelID

WITH RowNumCTE AS(
Select *,
	ROW_NUMBER() OVER (
	PARTITION BY ParcelID,
				 PropertyAddress,
				 SalePrice,
				 SaleDate,
				 LegalReference
				 ORDER BY
					UniqueID
					) row_num
From PortfolioProject..Sheet1$
)
Select *
From RowNumCTE
Where row_num > 1
Order by PropertyAddress

-- Deletes Rows (Make sure that the entire query is selected or you will delete all the data)
WITH RowNumCTE AS(
Select *,
	ROW_NUMBER() OVER (
	PARTITION BY ParcelID,
				 PropertyAddress,
				 SalePrice,
				 SaleDate,
				 LegalReference
				 ORDER BY
					UniqueID
					) row_num
From PortfolioProject..Sheet1$
)
DELETE
From RowNumCTE
Where row_num > 1
-------------------------------------------------------------------------------------------------

-- Delete Unused Columns

Select *
From PortfolioProject..Sheet1$

ALTER TABLE PortfolioProject..Sheet1$
DROP COLUMN OwnerAddress, TaxDistrict, PropertyAddress, SaleDareConverted, PorpertySplitCity

ALTER TABLE PortfolioProject..Sheet1$
DROP COLUMN SaleDate