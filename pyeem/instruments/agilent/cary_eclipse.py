import pandas as pd


class CaryEclipse:
    """The Cary Eclipse Fluorescence Spectrophotometer."""

    manufacturer = "Agilent"
    """Name of Manufacturer."""

    name = "cary_eclipse"
    """Name of Instrument."""

    supported_models = ["Cary Eclipse"]
    """List of supported models."""

    def __init__(self, model, sn=None):
        """
        Args:
            model (str): The model name of the instrument.
            sn (str or int, optional): The serial number of the instrument. Defaults to None.
        """
        self.model = model
        self.sn = sn

    @staticmethod
    def load_eem(filepath):
        """Loads an Excitation Emission Matrix which is generated by the instrument.

        Args:
            filepath (str): The filepath of the data file.

        Returns:
            pandas.DataFrame: An Excitation Emission Matrix.
        """
        # Read csv, skip the 2nd row which contains repeating
        # columns pairs of "Wavelength (nm)", "Intensity (a.u.)"
        # df = pd.read_csv("sample_3D.csv", skiprows=[1])
        df = pd.read_csv(filepath, skiprows=[1])

        # Drop columns and rows with all NaN values, these sometimes
        # appear at the end for some reason
        df.dropna(how="all", axis=1, inplace=True)
        df.dropna(how="all", axis=0, inplace=True)

        # Get the columns and extract the first one
        # We'll use the first one to remove all rows below
        # the actual EEM. These rows are filled with metadata about
        # each excitation scan. We'll throw them away for the point being.
        columns = df.columns.tolist()
        first_ex_wl = columns[0]
        df[first_ex_wl] = df[first_ex_wl].apply(pd.to_numeric, errors="coerce")
        df.drop(df.loc[pd.isna(df[first_ex_wl]), :].index, inplace=True)

        # Due to the very odd format of the raw EEM, there is an emission wavelength
        # column and an intensity column for each excitation wavelength.
        # Maybe the emission wavelengths can be changed between excitation scans and that's
        # why it is stored in that format. Regardless, what we want is an index containing emission
        # wavelengths and column names which are excitation wavelengths.

        # We zip together excitation column names and the corresponding intensity columns
        zipped = dict(zip(columns[1::2], columns[0::2]))

        # Force all columns to be numeric
        df[columns] = df[columns].apply(pd.to_numeric, errors="coerce")

        # We will only keep the emission wavelengths that correspond with the first excitation scan.
        # These emission wavelengths should correspond with all of the excitation scans, assuming this
        # setting is not changed between excitation scans. Which should be true.
        em_wls = df[first_ex_wl]
        em_wls.name = "emission_wavelength"
        em_wls.index.name = "emission_wavelength"

        # Get the excitation column names and drop them from the dataframe
        # Since these columns only contain emission wavelengths and we
        # already extracted the emission wavelengths for the first excitation scan
        # which we will use for all the scans.
        ex_cols = [col for col in columns if "_EX_" in col]
        df.drop(columns=ex_cols, inplace=True)

        # Rename the emission intensity columns to their corresponding
        # excitation wavelength in order to get Emission (rows) by Excitation (cols)
        df.rename(columns=zipped, inplace=True)
        # Remove the additional substring preprended to each excitation wavelength.
        new_cols = df.columns.str.rsplit("_", 1)
        new_cols = [i[-1] for i in new_cols.to_list()]
        df.columns = new_cols
        df.columns = df.columns.astype(float)

        # Set the index of the dataframe to be the emission wavelengths
        df.set_index([pd.Index(em_wls)], inplace=True)
        return df

    @staticmethod
    def load_absorbance(filepath):
        """Loads an absorbance spectrum which is generated by the instrument.

        Args:
            filepath (str): The filepath of the data file.

        Returns:
            pandas.DataFrame: An absorbance spectrum.
        """
        absorb_df = pd.read_csv(
            filepath, header=1, usecols=["Wavelength (nm)", "Abs"], index_col=False
        )
        nan_rows = [i for i, x in enumerate(absorb_df.iloc[:, 1].isna()) if x]
        if nan_rows:
            absorb_df = absorb_df.iloc[: (nan_rows[0] - 1)]
        absorb_df = absorb_df.rename(
            columns={"Wavelength (nm)": "excitation_wavelength", "Abs": "absorbance"}
        )
        absorb_df[absorb_df.columns] = absorb_df[absorb_df.columns].apply(
            pd.to_numeric, errors="coerce", axis=1
        )
        absorb_df.set_index("excitation_wavelength", inplace=True)
        absorb_df = absorb_df.sort_index()
        absorb_df.index = absorb_df.index.astype("float64")
        return absorb_df

    @staticmethod
    def load_water_raman(filepath):
        """Loads a water Raman spectrum which is generated by the instrument.

        Args:
            filepath (str): The filepath of the data file.

        Raises:
            NotImplementedError: On the TODO list...
        """
        raman_df = pd.read_csv(
            filepath,
            header=1,
            usecols=["Wavelength (nm)", "Intensity (a.u.)"],
            index_col=False,
        )
        raman_df = raman_df.iloc[
            : ([i for i, x in enumerate(raman_df.iloc[:, 1].isna()) if x][0] - 1)
        ]
        raman_df[raman_df.columns] = raman_df[raman_df.columns].apply(
            pd.to_numeric, errors="coerce", axis=1
        )
        raman_df = raman_df.rename(
            columns={
                "Intensity (a.u.)": "intensity",
                "Wavelength (nm)": "emission_wavelength",
            }
        )
        raman_df.set_index("emission_wavelength", inplace=True)
        return raman_df

    @staticmethod
    def load_spectral_corrections():
        """TODO - Should load instrument specific spectral corrections which will be used in data preprocessing.

        Raises:
            NotImplementedError: On the TODO list...
        """
        raise NotImplementedError()
