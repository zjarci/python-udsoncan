from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class SecurityAccess(BaseService):
	_sid = 0x27

	supported_negative_response = [	Response.Code.SubFunctionNotSupported, 
							Response.Code.IncorrectMessageLegthOrInvalidFormat,
							Response.Code.ConditionsNotCorrect,
							Response.Code.RequestSequenceError,
							Response.Code.RequestOutOfRange,
							Response.Code.InvalidKey,
							Response.Code.ExceedNumberOfAttempts,
							Response.Code.RequiredTimeDelayNotExpired
							]

	class Mode:
		RequestSeed=0
		SendKey=1

	@classmethod 
	def normalize_level(cls, mode, level):
		cls.validate_mode(mode)
		ServiceHelper.validate_int(level, min=0, max=0x7F, name='Security level')

		if mode == cls.Mode.RequestSeed:
			return level if level % 2 == 1 else level-1
		elif mode == cls.Mode.SendKey:
			return level if level % 2 == 0 else level+1

	@classmethod
	def make_request(cls, level, mode=Mode.RequestSeed, key=None):
		from udsoncan import Request
		cls.validate_mode(mode)

		ServiceHelper.validate_int(level, min=0, max=0x7F, name='Security level')
		req = Request(service=cls, subfunction=cls.normalize_level(mode=mode, level=level))

		if mode == cls.Mode.SendKey:
			if not isinstance(key, bytes):
				raise ValueError('key must be a valid bytes object')
			req.data = key

		return req

	@classmethod
	def interpret_response(cls, response, mode):
		cls.validate_mode(mode)

		response.service_data = cls.ResponseData()
		minlength = 2 if mode == cls.Mode.RequestSeed else 1

		if len(response.data) < minlength:
				raise InvalidResponseException(response, "Response data must be at least %d bytes" % (minlength))
		
		response.service_data.security_level_echo = response.data[0]

		if mode == cls.Mode.RequestSeed:
			response.service_data.seed = response.data[1:]

	@classmethod
	def validate_mode(cls, mode):
		if mode not in [cls.Mode.RequestSeed, cls.Mode.SendKey]:
			raise ValueError('Given mode must be either be RequestSeed (0) or SendKey (1).')

	class ResponseData(BaseResponseData):
		def __init__(self):
			super().__init__(SecurityAccess)

			self.security_level_echo = None
			self.seed = None