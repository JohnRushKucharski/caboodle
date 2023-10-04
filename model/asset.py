'''A model for depreciating assets.'''
from random import uniform
from dataclasses import dataclass

@dataclass
class Asset:
    '''A depreciating asset.'''
    initial_value: float = 100.0
    '''New or replacement asset value.'''
    salvage_value: float = 0.0
    '''Value of asset at end of depreciation schedule.'''
    periods_in_schedule: float = 100.0
    '''Number of periods in depreciation schedule.'''
    maintenance_requirement: float = 1.0
    '''Maintenance requirement per time period.'''
    shape_parameter: float = 1.0
    '''
    Parameter controling shape of depreciation schedule. 1.0 by default.
    
    Notes:
        0.0 is constant (no depreciation),
        1.0 is linear, 
        > 1.0 is concave, 
        < 1.0 is convex
    '''
    acceleration_factor: float = 1.0
    '''
    Parameter controlling acceleration of depreciation schedule, 
    when schedules maintenance is not performed. 1.0 by default.
    
    Notes:
        1.0 is linear acceleration,
    '''

    def ft(self, t: float) -> float:  # pylint: disable=invalid-name
        '''
        Portion depreciable asset value remaining as function of time.
        
        Args:
            t (float): time period in depreciation schedule.
            
        Returns:
            float: portion of depreciable asset value remaining.
        '''
        if self.periods_in_schedule <= t:
            # prevents a negative result.
            return 0.0
        return (1 - t / self.periods_in_schedule) ** self.shape_parameter

    def inverse_ft(self, y: float) -> float:  # pylint: disable=invalid-name
        '''
        Time period in schedule corresponding to given portion of depreciable asset value.
        
        Args:
            y (float): portion of depreciable asset value remaining.
        
        Returns:
            float: time period in depreciation schedule.
        '''
        if not 0.0 <= y <= 1.0:
            # prevents a complex result, or non-sense y values.
            raise ValueError(f'y: {y} must be between 0.0 and 1.0.')
        return self.periods_in_schedule * (1 - y ** (1 /  self.shape_parameter))

    def scheduler(self, maintenance: float) -> float:
        '''
        Computes time period of depreciation for a given maintenance level.

        Args:
            maintenance (float): maintenance level.
            asset (Asset): asset to be depreciated.
            acceleration (float): acceleration of depreciation schedule, 1.0 is no acceleration.

        Raises:
            ValueError: if maintenance exceeds maintenance requirement, there is no benefit to overfunding maintenance, for this use repairs.  # pylint: disable=line-too-long

        Returns:
            float: time periods of depreciation.
        '''
        if self.maintenance_requirement < maintenance:
            raise ValueError('Maintenance exceeds maintenance requirement.')
        return 1 + (self.maintenance_requirement - maintenance) / self.maintenance_requirement * self.acceleration_factor # pylint: disable=line-too-long

    def depreciate(self, asset_value: float, maintenance: float = 0.0) -> float:
        '''Depreciates asset value based on encapsulated depreciation schedule and maintenance level.  # pylint: disable=line-too-long

        Args:
            asset_value (float): the current value of the asset.
            maintenance (float, optional): maintenance level. If maintenance > asset.maintenance_requirement partial recapitalization occurs. Defaults to 0.0.  # pylint: disable=line-too-long

        Returns:
            float: the depreciated asset value.
        '''
        maint = min(maintenance, self.maintenance_requirement)
        recap = max(0.0, maintenance - self.maintenance_requirement)
        depreciable_value = self.initial_value - self.salvage_value
        t = self.inverse_ft(asset_value / depreciable_value) + self.scheduler(maintenance=maint)  # pylint: disable=invalid-name
        return max(min(self.initial_value, depreciable_value * self.ft(t) + recap), self.salvage_value)  # pylint: disable=line-too-long

    def shadow_value(self, last_estimate: float, actual_value: float,
                     maintenance: float, max_portion_error: float = 0.10) -> float:
        '''Estimates the value of an asset given its last estimated value and portion of maintenance funding.  # pylint: disable=line-too-long
        
        Args:
            last_estimate (float): the last estimated value of the asset.
            maintenance (float): maintenance funding provided.
            max_portion_error (float, optional): maximum portion depreciable value error, if portion_maintenance = 0. Defaults to 0.10. # pylint: disable=line-too-long
        
        Raises:
            ValueError: if portion_max_error is not between 0.0 and 1.0.
            
        Returns:
            float: the estimated asset value.
        '''
        if not 0.0 <= max_portion_error <= 1.0:
            raise ValueError('Maximum portion error must be between 0.0 and 1.0.')
        if maintenance <= self.maintenance_requirement:
            # too little maintenance increase error.
            error: float = (1 - maintenance / self.maintenance_requirement) * max_portion_error  # pylint: disable=line-too-long
            new_estimate = last_estimate + uniform(-error, error) * (self.initial_value - self.salvage_value)  # pylint: disable=line-too-long
        else:
            # decrease error by amount of recapitalization
            error = actual_value - last_estimate
            recap = maintenance - self.maintenance_requirement
            if recap < abs(error):
                new_estimate = last_estimate + recap if last_estimate < actual_value else last_estimate - recap  # pylint: disable=line-too-long
            else:
                # recapitalization is greater than error
                new_estimate = actual_value
        return min(max(self.salvage_value, new_estimate), self.initial_value)

    def portion_remaining(self, asset_value: float) -> float:
        '''Computes portion of depreciable value remaining given an asset value.'''
        if not self.salvage_value <= asset_value <= self.initial_value:
            raise ValueError(f'Asset value: {asset_value} must be between initial_value: {self.initial_value} and salvage value: {self.salvage_value}.')  # pylint: disable=line-too-long
        return max(0.0, (asset_value - self.salvage_value) / (self.initial_value - self.salvage_value))  # pylint: disable=line-too-long
        