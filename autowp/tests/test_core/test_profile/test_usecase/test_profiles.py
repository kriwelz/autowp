import unittest
import hashlib
from typing import Optional, List

from autowp.core.shared.utils import typechecker
from autowp.core.shared.exceptions import VarTypeError
from autowp.core.shared.base import PasswordHasher

from autowp.core.profile.entity import Profile, Password
from autowp.core.profile.repository import ProfileRepository, Options
from autowp.core.profile.usecase.register import RegisterUseCase
from autowp.core.profile.usecase.profiles import ProfilesUseCase 

class Sha256Hasher(PasswordHasher):

	def hash(self) -> str:
		hasher = hashlib.new('sha256')
		if self.raw != '':
			hasher.update(self.raw.encode())
			return hasher.hexdigest()

		return self.raw

class MemoryProfileRepo(ProfileRepository):

	def __init__(self):
		self.in_memory = {}

	def create(self, profile: Profile) -> Profile:
		self.in_memory[profile.name] = profile
		return profile 

	def get_list(self, options: Optional[Options] = None) -> Optional[List[Profile]]:
		if not options:
			return None

		if 'names' in options:
			names = options.get('names')
			if isinstance(names, list):
				data = []
				for name in names:
					if name in self.in_memory:
						data.append(self.in_memory.get(name))

				if len(data) >= 1:
					return data
		
		return None

	def get_detail(self, name: str) -> Optional[Profile]:
		if name in self.in_memory:
			return self.in_memory.get(name)

		return None
	
	def id(self, id: str) -> Optional[Profile]:
		pass

	def remove(self, name: str) -> bool:
		typechecker.check(name, str, ('name', 'str'))

		check = self.get_detail(name)
		if check:
			del self.in_memory[name]
			return True

		return False 

class ProfilesUseCaseTestCase(unittest.TestCase):

	def test_get_list_success(self):
		repo = MemoryProfileRepo()
		profile1 = Profile('myname', Password('mypassword', Sha256Hasher))
		profile2 = Profile('myname2', Password('mypassword', Sha256Hasher))
		
		register_case = RegisterUseCase(repo)
		register_case.register(profile1)
		register_case.register(profile2)

		profiles_case = ProfilesUseCase(repo)
		profiles = profiles_case.profiles({'names': ['myname', 'myname2']})

		self.assertEqual(2, len(profiles))
		
		profile1_from_db = profiles[0]
		self.assertEqual('myname', profile1_from_db.name)

	def test_get_list_none(self):
		repo = MemoryProfileRepo()
		profiles_case = ProfilesUseCase(repo)
		profiles = profiles_case.profiles({'names': []})

		self.assertIsNone(profiles)
