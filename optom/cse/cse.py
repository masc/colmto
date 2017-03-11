# -*- coding: utf-8 -*-
# @package optom.cse
# @cond LICENSE
# #############################################################################
# # LGPL License                                                              #
# #                                                                           #
# # This file is part of the Optimisation of 2+1 Manoeuvres project.          #
# # Copyright (c) 2017, Malte Aschermann (malte.aschermann@tu-clausthal.de)   #
# # This program is free software: you can redistribute it and/or modify      #
# # it under the terms of the GNU Lesser General Public License as            #
# # published by the Free Software Foundation, either version 3 of the        #
# # License, or (at your option) any later version.                           #
# #                                                                           #
# # This program is distributed in the hope that it will be useful,           #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# # GNU Lesser General Public License for more details.                       #
# #                                                                           #
# # You should have received a copy of the GNU Lesser General Public License  #
# # along with this program. If not, see http://www.gnu.org/licenses/         #
# #############################################################################
# @endcond
# pylint: disable=too-few-public-methods
# pylint: disable=no-self-use
"""CSE classes"""
import optom.common.log
import optom.cse.policy


class BaseCSE(object):
    """Base class for the central optimisation entity (CSE)."""

    def __init__(self, args=None):
        """
        C'tor
        @param args: argparse configuration
        """
        if args is not None:
            self._log = optom.common.log.logger(__name__, args.loglevel, args.quiet, args.logfile)
        self._log = optom.common.log.logger(__name__)
        self._vehicles = set()
        self._policies = []

    @property
    def policies(self):
        """
        Policies of CSE
        Returns:
            policies tuple
        """
        return tuple(self._policies)

    def apply(self, vehicles):
        """
        Apply policies to vehicles
        @param vehicles: Iterable of vehicles or dictionary Id -> Vehicle
        @retval self
        """
        for i_vehicle in vehicles.itervalues() if isinstance(vehicles, dict) else vehicles:
            self.apply_one(i_vehicle)

        return self

    def apply_one(self, vehicle):
        """
        Apply policies to one vehicles
        @param vehicle: Vehicle
        @retval self
        """
        for i_policy in self._policies:
            if i_policy.applies_to(vehicle) \
                    and i_policy.behaviour == optom.cse.policy.BEHAVIOUR.deny:
                vehicle.change_vehicle_class(
                    optom.cse.policy.SUMOPolicy.to_disallowed_class()
                )
                return self

        # default case: no applicable policy found
        vehicle.change_vehicle_class(
            optom.cse.policy.SUMOPolicy.to_allowed_class()
        )

        return self


class SumoCSE(BaseCSE):
    """First-come-first-served CSE (basically do nothing and allow all vehicles access to OTL."""

    _valid_policies = {
        "SUMOUniversalPolicy": optom.cse.policy.SUMOUniversalPolicy,
        "SUMONullPolicy": optom.cse.policy.SUMONullPolicy,
        "SUMOSpeedPolicy": optom.cse.policy.SUMOSpeedPolicy,
        "SUMOPositionPolicy": optom.cse.policy.SUMOPositionPolicy,
        "SUMOVTypePolicy": optom.cse.policy.SUMOVTypePolicy
    }

    def add_policy(self, policy, policy_cfg=None):
        """
        Add policy to SumoCSE.
        @param policy: policy object
        @param policy_cfg: policy configuration
        @retval self
        """

        if not isinstance(policy, optom.cse.policy.SUMOVehiclePolicy):
            raise TypeError

        if policy_cfg is not None \
                and policy_cfg.get("vehicle_policies", {}).get("rule", False):
            # look for sub-policies
            policy.rule = policy_cfg.get("vehicle_policies", {}).get("rule")
            for i_subpolicy in policy_cfg.get("vehicle_policies", {}).get("policies", []):
                policy.add_vehicle_policy(
                    self._valid_policies.get(i_subpolicy.get("type"))(
                        behaviour=optom.cse.policy.BasePolicy.behaviour_from_string_or_else(
                            i_subpolicy.get("behaviour"),
                            optom.cse.policy.BEHAVIOUR.deny
                        ),
                        **i_subpolicy.get("args")
                    )
                )

        self._policies.append(
            policy
        )

        return self

    def add_policies_from_cfg(self, policies_config):
        """
        Add policies to SumoCSE based on run config's "policies" section.
        @param policies_config: run config's "policies" section
        @retval self
        """

        if policies_config is None:
            return self

        for i_policy in policies_config:
            self.add_policy(
                self._valid_policies.get(i_policy.get("type"))(
                    behaviour=optom.cse.policy.BasePolicy.behaviour_from_string_or_else(
                        i_policy.get("behaviour"),
                        optom.cse.policy.BEHAVIOUR.deny
                    ),
                    **i_policy.get("args")
                ),
                i_policy
            )

        return self
